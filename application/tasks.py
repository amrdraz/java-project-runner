"""
Defines Celery instance and tasks.
"""
from application import app, db
from application.models import Submission, Project, User
from application.junit import setup_junit_dir, parse_junit_results
from flask.ext.sendmail import Mail, Message
from flask import render_template
from celery import Celery
from shutil import rmtree
import os
import re
import subprocess32 as subprocess
from tempfile import mkdtemp

mail = Mail(app)

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
def activation_mail_task(user_id):
    """
    Sends an activation email.
    """
    try: 
        user = User.objects.get(id=user_id)
        # Generate link
        activation_token = user.generate_activation_token()
        activation_url = 'https//evaluator.in/activate/?token={0}'.format(activation_token)
        # send email
        msg = Message("Activate your evaluator.in account")
        msg.add_recipient(user.email)
        msg.sender = "no-reply@evaluator.in"
        context = {'user': user.to_dict(), 'activation_url': activation_url}
        msg.body = render_template('emails/activation.txt', **context)
        mail.send(msg)
    except (db.DoesNotExist):
        app.logger.warning('Attempted to send mail to non existing user.')

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
        # Create a temporary directories
        working_directory = mkdtemp()
        selinux_tmp = mkdtemp()

        # Populate directory
        renamed_files, has_tests = setup_junit_dir(
            subm, proj, working_directory)
        
        command = ['sandbox', '-M', '-H', working_directory, '-T', selinux_tmp,
                   'bash', renamed_files.get(app.config['ANT_RUN_FILE_NAME'],
                    app.config['ANT_RUN_FILE_NAME'])]
        # Actually Run the command
        
        app.logger.info('Launching {0}'.format(' '.join(command)))

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # communicate waits for the process to finish
        stdout, stderr = process.communicate()
        subm.compile_status = 'Compile failed' not in stderr
        app.logger.info(stderr)
        app.logger.info(stdout)
        subm.compiler_out = stdout
        subm.safe_save()
        ant_build_dir_name = renamed_files.get(
                app.config['ANT_BUILD_DIR_NAME'], app.config['ANT_BUILD_DIR_NAME'])
        # If some other error occured and for some reason ant didn't even run
        subm.compile_status &= ant_build_dir_name in os.listdir(working_directory)
        if subm.compile_status and has_tests:
            # Parse test output
            tests = os.path.join(working_directory, ant_build_dir_name)
            tests = os.path.join(tests, 'tests')
            parse_junit_results(tests, subm)
            
        rmtree(working_directory)
        rmtree(selinux_tmp)
        subm.processed = True
        subm.safe_save()
    except db.DoesNotExist:
        app.logger.warning(
            'Junit task launched with invalid submission_id {0}.'.format(submission_id))
    except:
        app.logger.error('Unforseen error while processing {0}'.format(submission_id))
        subm.processed = True
        subm.compile_status = False
        subm.safe_save()
