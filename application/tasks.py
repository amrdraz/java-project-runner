"""
Defines Celery instance and tasks.
"""
from application import app, db
from application.models import Submission, Project
from application.junit import setup_junit_dir, parse_junit_results
from celery import Celery
from shutil import rmtree
import os
import re
import subprocess
from tempfile import mkdtemp


def make_celery(app):
    """
    Creates and configures celery instance.
    """
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



@celery.task
def junit_task(submission_id):
    """
    Processes a junit submission.
    """
    try:
        app.logger.info('Starting Junit for {0}'.format(submission_id))
        subm = Submission.objects.get(id=submission_id)
        proj = Project.objects.get(submissions=subm)
        if subm.processed:
            app.logger.warning(
                'Junit task launched with processed submission, id: {0}.'.format(submission_id))
            return
        # Create a temporary directory
        working_directory = mkdtemp()

        # Populate directory
        renamed_files, has_tests = setup_junit_dir(
            subm, proj, working_directory)
        selinux_tmp = mkdtemp()
        command = ['sandbox', '-M', '-H', working_directory, '-T', selinux_tmp,
                   'bash', renamed_files.get(app.config['ANT_RUN_FILE_NAME'], app.config['ANT_RUN_FILE_NAME'])]
        # Actually Run the command
        os.chdir(working_directory)
        app.logger.info('Launching {0}'.format(' '.join(command)))
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.wait()
        subm.compile_status = 'Compile failed' not in stderr
        app.logger.info(stderr)
        app.logger.info(stdout)
        subm.compiler_out = stdout
        subm.save()
        app.logger.info(os.listdir(working_directory))
        if subm.compile_status and has_tests:
            # Parse test output
            tests = os.path.join(working_directory, renamed_files.get(
                app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME']))
            tests = os.path.join(tests, 'tests')
            parse_junit_results(tests, subm)
            

        rmtree(working_directory)
        rmtree(selinux_tmp)
        subm.processed = True
        subm.save()
    except db.DoesNotExist:
        app.logger.warning(
            'Junit task launched with invalid submission_id {0}.'.format(submission_id))
    except:
        app.logger.error('Unforseen error while processing {0}'.format(submission_id))
        subm.processed = True
        subm.compile_status = False
        subm.save()
