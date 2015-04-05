"""
Helpers for processing JUnit evaluations.
"""
import os
import stat
import patoolib
import glob
import subprocess32 as subprocess
from application import app
from application.models import TestResult, TestCase
from flask import render_template
from shutil import move
import xml.etree.ElementTree as ET
from shutil import rmtree
from tempfile import mkdtemp


class Enumerator(object):

    """Simple enumerator for the lowercase ascii alphabet."""

    def __init__(self, banned_words_list):
        self.token = ['a']
        self.symbol_table = set()
        for word in banned_words_list:
            self.symbol_table.add(word)

    def get_token(self):
        while "".join(self.token) in self.symbol_table:
            self.increment_token()
        token = "".join(self.token)
        self.symbol_table.add(token)
        self.increment_token()
        return token

    def increment_token(self):
        if self.token[-1] != 'z':
            self.token[-1] = chr(ord(self.token[-1]) + 1)
        elif len(self.token) == 1:
            self.token = ['a', 'a']
        else:
            # Either all chars are 'z' or one can be
            if all([x == 'z' for x in self.token]):
                self.token.append('a')
            else:
                # Go back recursively
                self.increment_helper()

    def increment_helper(self):
        if self.token[-1] != 'z':
            self.token[-1] = chr(ord(self.token[-1]) + 1)
            self.token.append('a')
        else:
            self.token = self.token[:-1]
            self.increment_helper()


class DirectoryError(Exception):

    def __init__(self, value):
        self.value = value
        super(DirectoryError, self).__init__()


class SRCError(Exception):

    def __init__(self, value):
        self.value = value
        super(SRCError, self).__init__()


def copy_junit_tests(project, working_directory, buffer_size):
    """
    Creates JUNIT directory structure.
    """
    tests_dir = os.path.join(
        working_directory, app.config['ANT_TESTS_DIR_NAME'])
    app.logger.info('using {0} as test directory initially'.format(tests_dir))
    os.mkdir(tests_dir)
    # Write each junit in the project to the tests dir
    for junit in project.tests:
        with open(os.path.join(tests_dir, junit.filename), "wb") as outfile:
            buff = junit.read(buffer_size)
            while len(buff) != 0:
                outfile.write(buff)
                buff = junit.read(buffer_size)


def prepare_for_source(submission, enumerator, in_use_names, working_directory):
    """
    Makes sure the source archive can be written without overwriting any existing files.
    returns dict of renamed files.
    Doesn't rename source archive.
    """
    renamed_files = {}
    src_arch_name = submission.code.get().filename
    src_arch_name_split = src_arch_name.split('.')
    arch_no_ext_nm = src_arch_name_split[0]
    abs_arch_no_ext_nm = os.path.join(working_directory, arch_no_ext_nm)
    if arch_no_ext_nm in in_use_names:
        renamed_files[arch_no_ext_nm] = enumerator.get_token()
        move(abs_arch_no_ext_nm, os.path.join(
            working_directory, renamed_files[arch_no_ext_nm]))
    if src_arch_name in in_use_names and src_arch_name != arch_no_ext_nm:
        renamed_files[src_arch_name] = enumerator.get_token()
        move(abs_arch_no_ext_nm, os.path.join(
            working_directory, renamed_files[src_arch_name]))
    return renamed_files


def extract_source(submission, working_directory, buffer_size):
    """Writes the source archive and extracts it."""
    # Copy archive
    abs_arch_name = os.path.join(
        working_directory, submission.code.get().filename)
    prev_entry_count = len(os.listdir(working_directory))
    with open(abs_arch_name, "wb") as archive_out:
        buff = submission.code.read(buffer_size)
        while len(buff) != 0:
            archive_out.write(buff)
            buff = submission.code.read(buffer_size)
    after_entry_count = len(os.listdir(working_directory))
    if after_entry_count < prev_entry_count + 1:
        message = 'Working directory entry count assertion failed. Before write {0} after write {1}'.format(
            prev_entry_count, after_entry_count)
        app.logger.error(message)
        raise DirectoryError(message)
    # Extract archive
    prev_entry_count = after_entry_count
    patoolib.extract_archive(abs_arch_name, outdir=working_directory)
    after_entry_count = len(os.listdir(working_directory))
    os.remove(abs_arch_name)
    if after_entry_count < prev_entry_count + 1:
        message = 'Working directory entry count assertion failed. Before extraction {0} after extraction {1}'.format(
            prev_entry_count, after_entry_count)
        app.logger.error(message)
        raise DirectoryError(message)


def determine_src_dir(in_use_names, renamed_files, working_directory):
    """Attempts to determine source directory name"""
    candidates = [entry for entry in os.listdir(working_directory)
                  if (entry not in in_use_names) and (entry not in renamed_files.values())]

    if len(candidates) != 1:
        message = 'Could not determine working directory. Candidates {0},\ndirectory entries{1},\nrenamed_files {2},\nin_use_names: {1}'
        message = message.format(','.join(candidates), ','.join(os.listdir(
            working_directory)), ','.join(renamed_files.items()), ','.join(in_use_names))
        app.logger.error(message)
        raise SRCError(message)
    else:
        return candidates[0]


def create_ant_build_file(project, in_use_names, renamed_files, working_directory):
    """Creates ant build file."""
    src_dir = determine_src_dir(in_use_names, renamed_files, working_directory)
    # Paths in build.xml are relative not absolute.
    context = {
        "src_dir": src_dir,
        "tests_dir": renamed_files.get(app.config['ANT_TESTS_DIR_NAME'], app.config['ANT_TESTS_DIR_NAME']),
        "plain_format": False,
        "xml_format": True,
        "build_dir": renamed_files.get(app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME']),
        "has_tests": project.has_tests,
        "working_directory": working_directory,
        "test_classes" : [test.filename.replace('.java', '.class') for test in project.tests],
        "test_files": [test.filename for test in project.tests]
    }
    ant_build_template = render_template('runner/build.xml', **context)
    build_abs_fname = os.path.join(
        working_directory, renamed_files.get(app.config['ANT_BUILD_FILE_NAME'], app.config['ANT_BUILD_FILE_NAME']))
    with open(build_abs_fname, "w") as script_file:
        script_file.write(ant_build_template)


def create_ant_script_file(project, in_use_names, renamed_files, working_directory):
    """Creates ant script runner"""
    script_abs_fname = os.path.join(working_directory, renamed_files.get(
        app.config['ANT_RUN_FILE_NAME'], app.config['ANT_RUN_FILE_NAME']))
    context = {
        'buildfile_name': renamed_files.get(app.config['ANT_BUILD_FILE_NAME'], app.config['ANT_BUILD_FILE_NAME']),
        'has_tests': project.has_tests,
        'test_timeout': project.test_timeout_seconds
    }
    rendered_script = render_template('runner/ant_script.sh', **context)
    with open(script_abs_fname, "w") as script_file:
        script_file.write(rendered_script)
    script_st = os.stat(script_abs_fname)
    os.chmod(script_abs_fname, script_st.st_mode | stat.S_IEXEC)


def setup_directory(submission, project, working_directory):
    """
    Sets up the directory layout.
    """
    BUFFER_SIZE = app.config['FILE_BUFFER_SIZE']
    if project.has_tests:
        copy_junit_tests(project, working_directory, BUFFER_SIZE)

    # Check if archive clashes
    in_use_names = os.listdir(working_directory) + [app.config[
        'ANT_BUILD_FILE_NAME'] + app.config['ANT_RUN_FILE_NAME'] + app.config['ANT_BUILD_DIR_NAME']]
    enumerator = Enumerator(in_use_names)
    renamed_files = prepare_for_source(
        submission, enumerator, in_use_names, working_directory)
    extract_source(submission, working_directory, BUFFER_SIZE)
    app.logger.info('Directory after extraction:[{0}]'.format(
        ','.join(os.listdir(working_directory))))
    before_ant_scripts = len(os.listdir(working_directory))
    create_ant_build_file(
        project, in_use_names, renamed_files, working_directory)
    create_ant_script_file(
        project, in_use_names, renamed_files, working_directory)
    after_ant_scripts = len(os.listdir(working_directory))
    if after_ant_scripts != before_ant_scripts + 1:
        message = 'Failed before and after sanity check for ant scripts entries: {0}'.format(
            ','.join(os.listdir(working_directory)))
        app.logger.error(message)
    return renamed_files


def parse_junit_results(test_res_dir, subm):
    """
    Parses XML output. Creates embedded TestResult and TestCase documents.
    Doesn't save submission.
    param: ters_res_dir path to directory where reports are.
    param: subm submission document instance.
    """
    files = glob.glob(os.path.join(test_res_dir, '*.xml'))
    test_results = {}
    for junit_report in files:
        # Process each junit report
        tree = ET.parse(junit_report)
        for test_case_elm in tree.iterfind('testcase'):
            # Process each test case in a junit file
            class_name = test_case_elm.attrib['classname']
            # class name is something like FooTest which is the class
            # the tests were declared at
            if class_name not in test_results:
                # Create new result if needed
                test_results[class_name] = TestResult(
                    name=class_name, success=True)
            # Populate case
            case = TestCase(
                name=test_case_elm.attrib['name'], passed=True, detail='')
            for failure in test_case_elm.iterfind('failure'):
                # If it has a failure child then it failed.
                case.passed = False
                case.detail += failure.text + '\n'
            for err in test_case_elm.iterfind('error'):
                # If it has an error child then it failed.
                case.passed = False
                case.error = True
                case.detail += err.text + '\n'
            case.save()
            test_results[class_name].cases.append(case)
            test_results[class_name].success &= case.passed

    subm.test_results = test_results.values()
    for r in subm.test_results:
        r.save()
    subm.save()


def run_sandbox(working_directory, selinux_directory, renamed_files, submission):
    """Initiates SELinux Sanbox."""
    command = ['sandbox', '-M', '-H', working_directory, '-T',
               selinux_directory, 'bash',
               renamed_files.get(app.config['ANT_RUN_FILE_NAME'], app.config['ANT_RUN_FILE_NAME'])]
    app.logger.info('Lauching {0}'.format(' '.join(command)))
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    submission.compile_status = ('THE SOURCE WAS COMPILED SUCCESFULLY' 
        in stderr or 'THE SOURCE WAS COMPILED SUCCESFULLY' in stdout)
    app.logger.info(stderr)
    app.logger.info(stdout)
    submission.compiler_out = stderr + '\n' + stdout
    ant_build_dir_name = renamed_files.get(
        app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME'])
    if submission.compile_status and not ant_build_dir_name in os.listdir(working_directory):
        app.logger.error('Error unknown reason for compilation faliure.')
    submission.compile_status &= ant_build_dir_name in os.listdir(
        working_directory)


def junit_submission(submission, project):
    # First we need to create the temporary directories

    class TempDirectories(object):

        def __enter__(self):
            self.dirs = mkdtemp(), mkdtemp()
            return self.dirs

        def __exit__(self, type, value, traceback):
            if app.config['CLEAN_TEMP_DIRS']:
                rmtree(self.dirs[0])
                rmtree(self.dirs[1])

    with TempDirectories() as directories:
        try:
            working_directory, selinux_directory = directories
            app.logger.info('using {0} and {1} as directories'.format(working_directory, selinux_directory))
            # Populate directory
            renamed_files = setup_directory(
                submission, project, working_directory)
            run_sandbox(
                working_directory, selinux_directory, renamed_files, submission)
            if submission.compile_status and project.has_tests:
                tests_dir = os.path.join(working_directory, 
                    renamed_files.get(app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME']))
                tests_dir = os.path.join(tests_dir, 'tests')
                parse_junit_results(tests_dir, submission)
            submission.processed = True
            submission.save()
        except DirectoryError as de:
            submission.compile_status = False
            submission.processed = True
            submission.compiler_out = de.value
            submission.save()
        except SRCError as se:
            submission.compile_status = False
            submission.compiler_out = se.value
            submission.processed = True
            submission.save()
