"""
Defines Celery instance and tasks.
"""
from application import app, db
from celery import Celery
import application.mail_tasks as mtasks
from application.models import Submission, Project
from application.junit import junit_submission
import datetime





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
def send_random_password(user_id):
    """
    Generates and sends a new random password.
    """
    mtasks.random_password(user_id)



@celery.task
def password_reset_mail_task(user_id):
    """
    Sends a password reset mail.
    """
    mtasks.reset_password(user_id)

@celery.task
def activation_mail_task(user_id):
    """
    Sends an activation email.
    """
    mtasks.activate_account(user_id)

@celery.task
def junit_task(submission_id):
    """
    Processes a junit submission.
    """
    try:
        app.logger.info('Starting Junit for {0}'.format(submission_id))
        submission = Submission.objects.get(id=submission_id)
        project = Project.objects.get(submissions=submission)
        if submission.processed:
            app.logger.warning(
                'Junit task launched with processed submission, id: {0}.'.format(submission_id))
        junit_submission(submission, project)
        for sub in [s for s in Submission.objects(submitter=submission.submitter, project=submission.project).order_by('-created_at')[10:] if s.processed]:
            sub.delete()
    except db.DoesNotExist:
        app.logger.warning(
            'Junit task launched with invalid submission_id {0}.'.format(submission_id))
    except Exception as e:
        app.logger.error('Unforseen error while processing {0}'.format(submission_id))
        app.logger.error('Exception {0}'.format(e))
        submission.processed = True
        submission.compile_status = False
        submission.compiler_out = 'Unforseen error occured while processing, please tell someone {0}'.format(e)
        submission.save()
