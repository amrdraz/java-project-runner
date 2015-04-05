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
def compute_team_grades(project_id, rerun_submissions):
    """
    Computes project ids.
    """
    app.logger.info('Starting grade computation for {0}'.format(project_id))
    Project.objects.get(id=project_id).grade_teams(rerun_submissions)
    app.logger.info('Computed grades for {0}'.format(project_id))

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


def junit_actual(submission_id):
    """
    Processes a junit submission.
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        app.logger.info('Starting Junit for {0}'.format(submission.id))
        project = submission.project
        if submission.processed:
            app.logger.warning(
                'Junit task launched with processed submission, id: {0}.'
                .format(submission_id))
            for result in submission.test_results:
                for case in result.cases:
                    case.delete()
                result.delete()
        submission.started_processing_at = datetime.datetime.utcnow()
        submission.save()
        junit_submission(submission, project)
        submission.finished_processing_at = datetime.datetime.utcnow()
        submission.save()
        return submission
    except db.DoesNotExist:
        app.logger.warning(
            'Junit task launched with invalid submission_id {0}.'
            .format(submission_id))
        return None
    except Exception as e:
        app.logger.error('Unforseen error while processing {0}'
                         .format(submission_id))
        app.logger.error('Exception {0}'.format(e))
        submission.processed = True
        submission.compile_status = False
        submission.compiler_out = (
            'Unforseen error occured while processing, please tell someone {0}'
            .format(e))
        submission.finished_processing_at = datetime.datetime.utcnow()
        submission.save()
        return None


@celery.task
def junit_task(submission_id):
    submission = junit_actual(submission_id)
    if submission is not None:
        for sub in [s for s
                    in Submission.objects(
                        submitter=submission.submitter,
                        project=submission.project,
                        processed=True).order_by('-created_at')[10:]]:
            app.logger.info(
                'Deleting submission id {0}, submitter {1}, project {2}'
                .format(sub.id, sub.submitter.name, sub.project.name))
            sub.delete()
            app.logger.info('Submission deleted')


@celery.task
def junit_no_deletion(submission_id):
    """
    Processes a junit submission, without deleting the older submissions.
    """
    junit_actual(submission_id)
