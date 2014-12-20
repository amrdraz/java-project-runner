from application import app, db
from celery import Celery
from models import Submission, Project
from flask import render_template
from shutil import rmtree, move
from subprocess import call
import patoolib
import fileinput
import os
import stat


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)



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


def setup_junit_dir(subm, working_directory):
    """
    Sets up test directory layout, generates ant build file and returns a dict of
    renamed files (build file or tests dir).
    dict is old_name: new_name, Important to note that names are relative
    """
    proj = Project.objects.get(submissions=subm)
    # TODO: Support other test frameworks and languages
    BUFFER_SIZE = app.config['FILE_SIZE']
    tests_dir = os.path.join(
        working_directory, app.config['ANT_TESTS_DIR_NAME'])
    os.mkdir(tests_dir)
    # Write each junit in the project to the tests dir
    for junit in proj.tests:
        with open(os.path.join(tests_dir, juinit.filename), "wb") as outfile:
            buff = junit.read(BUFFER_SIZE)
            while len(buff) != 0:
                outfile.write(buff)
                buff = junit.read(BUFFER_SIZE)

    # Extract submitted code
    src_arch_name = subm.code.filename
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
        "build_dir": renamed_files.get(app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME'])
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
        'buildfile_name': renamed_files.get(app.config['ANT_BUILD_FILE_NAME'], app.config['ANT_BUILD_FILE_NAME'])
    }
    rendered_script = render_template('runner/ant_script.sh', **context)
    with open(script_abs_fname, "w") as script_file:
        script_file.write(rendered_script)
    script_st = os.stat(script_abs_fname)
    os.chmod(script_abs_fname, script_st.st_mode | stat.S_IEXEC)
    return renamed_files


@celery.task
def juinit(submission_id):
    try:
        subm = Submission.objects.get(id=submission_id)
        if subm.processed:
            app.logger.warning(
                'Junit task launched with processed submission, id: {0}.'.format(submission_id))
            return
        # Create a temporary directory
        working_directory = mkdtemp()

        # Populate directory
        renamed_files = setup_junit_dir(subm, working_directory)
        selinux_tmp = mkdtemp()
        command = ['sandbox', '-M', '-H', working_directory, '-T', selinux_tmp,
                   'bash',
                   os.path.join(working_directory,
                                renamed_files.get(app.config['ANT_RUN_FILE_NAME'],
                                                  app.config['ANT_RUN_FILE_NAME']))]
        # Actually Run the command
        status = call(command)
        # TODO: Parse output
        subm.processed = True
        rmtree(working_directory)
        rmtree(selinux_tmp)
    except db.DoesNotExist:
        app.logger.warning(
            'Junit task launched with invalid submission_id {0}.'.format(submission_id))
