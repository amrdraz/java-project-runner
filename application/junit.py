"""
Helpers for processing JUnit evaluations.
"""
from application import app
from application.models import TestResult, TestCase
from flask import render_template
from shutil import move
import xml.etree.ElementTree as ET
import os
import stat
import patoolib
import glob


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


def copy_junit_tests(proj, working_directory, BUFFER_SIZE):
    """
    Creates JUNIT directory structure.
    """
    tests_dir = os.path.join(
        working_directory, app.config['ANT_TESTS_DIR_NAME'])
    os.mkdir(tests_dir)
    # Write each junit in the project to the tests dir
    for junit in proj.tests:
        with open(os.path.join(tests_dir, junit.filename), "wb") as outfile:
            buff = junit.read(BUFFER_SIZE)
            while len(buff) != 0:
                outfile.write(buff)
                buff = junit.read(BUFFER_SIZE)


def setup_junit_dir(subm, proj, working_directory):
    """
    Sets up test directory layout, generates ant build file and returns a dict of
    renamed files (build file or tests dir).
    dict is old_name: new_name, Important to note that names are relative
    """
    # TODO: Support other test frameworks and languages
    BUFFER_SIZE = app.config['FILE_BUFFER_SIZE']
    has_tests = len(proj.tests) >= 1
    if has_tests:
        copy_junit_tests(proj, working_directory, BUFFER_SIZE)
    # Extract submitted code
    src_arch_name = subm.code.get().filename
    abs_src_arch_name = os.path.join(working_directory, src_arch_name)
    src_arch_nm_split = src_arch_name.split('.')
    if len(src_arch_nm_split) > 1:
        arch_no_ext_nm = src_arch_nm_split[-2]
    else:
        arch_no_ext_nm = src_arch_nm_split[0]

    abs_arch_no_ext_nm = os.path.join(working_directory, arch_no_ext_nm)
    # Handle possible clashes
    # Handle them such that extracted code dir's name will not change
    in_use_names = os.listdir(
        working_directory) + [app.config['ANT_BUILD_FILE_NAME'] + app.config['ANT_RUN_FILE_NAME'] + app.config['ANT_BUILD_DIR_NAME']]
    enumerator = Enumerator(banned_words_list=in_use_names)
    renamed_files = {}
    if arch_no_ext_nm in in_use_names:
        # Generate new safe name
        # Top level are tests dir, build file and run file only
        renamed_files[arch_no_ext_nm] = enumerator.get_token()
        # Move file
        move(abs_arch_no_ext_nm,
             os.path.join(working_directory, renamed_files[working_directory]))

    # Write archive to directory
    with open(abs_src_arch_name, "wb") as code_outfile:
        buff = subm.code.read(BUFFER_SIZE)
        while len(buff) != 0:
            code_outfile.write(buff)
            buff = subm.code.read(BUFFER_SIZE)

    # Extract Archive
    patoolib.extract_archive(abs_src_arch_name, outdir=working_directory)
    os.remove(abs_src_arch_name)

    # Paths in build.xml are relevant not absolute
    context = {
        "src_dir": arch_no_ext_nm,
        "tests_dir": renamed_files.get(app.config['ANT_TESTS_DIR_NAME'], app.config['ANT_TESTS_DIR_NAME']),
        "plain_format": False,
        "xml_format": True,
        "build_dir": renamed_files.get(app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME']),
        "has_tests": has_tests
    }

    # Create template file
    ant_build_template = render_template('runner/build.xml', **context)

    build_abs_fname = os.path.join(
        working_directory, renamed_files.get(app.config['ANT_BUILD_FILE_NAME'], app.config['ANT_BUILD_FILE_NAME']))
    with open(build_abs_fname, "wb") as ant_build_file:
        ant_build_file.write(ant_build_template)
    # Render script
    script_abs_fname = os.path.join(working_directory, renamed_files.get(
        app.config['ANT_RUN_FILE_NAME'], app.config['ANT_RUN_FILE_NAME']))
    context = {
        'buildfile_name': renamed_files.get(app.config['ANT_BUILD_FILE_NAME'], app.config['ANT_BUILD_FILE_NAME']),
        'has_tests': has_tests,
        'test_timeout': proj.test_timeout_seconds
    }
    rendered_script = render_template('runner/ant_script.sh', **context)
    with open(script_abs_fname, "w") as script_file:
        script_file.write(rendered_script)

    script_st = os.stat(script_abs_fname)
    os.chmod(script_abs_fname, script_st.st_mode | stat.S_IEXEC)
    return renamed_files, has_tests



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
                test_results[class_name] = TestResult(name=class_name, success=True)
            # Populate case
            case = TestCase(name=test_case_elm.attrib['name'], passed=True, detail='')
            for failure in test_case_elm.iterfind('failure'):
                # If it has a failure child then it failed.
                case.passed = False
                case.detail += failure.text + '\n'
            for err in test_case_elm.iterfind('error'):
                # If it has a failure child then it failed.
                case.passed = False
                case.error = True
                case.detail += err.text + '\n'
            test_results[class_name].cases.append(case)
            test_results[class_name].success &= case.passed

    subm.test_results = test_results.values()
    

