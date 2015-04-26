"""
Defines Celery instance and tasks.
"""
from application import app, db
from celery import Celery
import application.mail_tasks as mtasks
from application.models import Submission, Project
from application.junit import junit_submission
import datetime
import shutil
import os
import fnmatch
import patoolib


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
def compute_team_grades(
        project_id,
        rerun_submissions=False,
        only_rerun_compile_error=False,
        get_latest=True):
    """
    Computes project ids.
    """
    app.logger.info('Starting grade computation for {0}'.format(project_id))
    Project.objects.get(id=project_id).grade_teams(
        rerun_submissions,
        only_rerun_compile_error,
        get_latest)
    app.logger.info('Computed grades for {0}'.format(project_id))


@celery.task
def rerun_submissions(
        project_id,
        email=None,
        only_rerun_compile_error=False,
        only_rerun_test_cases_zero=False,
        get_latest=True
        ):
    """
    Computes project ids.
    """
    app.logger.info('Starting submission rerun for {0}'.format(project_id))
    submissions = Project.objects.get(id=project_id).get_student_submissions(
                    True,
                    only_rerun_compile_error,
                    only_rerun_test_cases_zero,
                    get_latest)
    if email:
        mtasks.email_when_done(email, "ran "+str(len(submissions))+" submissions")
    app.logger.info('reran submissions for {0}'.format(project_id))


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


def extract_files_to_dirs(dir):
    dirs = []
    for file in os.listdir(dir):
        if (fnmatch.fnmatch(file, '*.zip') or fnmatch.fnmatch(file, '*.rar')):
            ext_dir = os.path.join(dir, file.split('.')[0])
            file_dir = os.path.join(dir, file)
            dirs.append(ext_dir)
            if not os.path.exists(ext_dir):
                os.makedirs(ext_dir)
            patoolib.extract_archive(file_dir, outdir=ext_dir)
    return dirs


def concat_java_projects(dirs, target_dir=None):
    for dir in dirs:
        concat_java_project(dir, target_dir)


def concat_java_project(dir, target_dir=None, outfilename=None):
    target_name = dir.split('/')[-1]
    target_dir = target_dir or os.path.abspath(dir, '..')
    outfilename = outfilename or os.path.join(target_dir, target_name+'.java')

    matches = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.java'):
            file = os.path.join(root, filename)
            if 'src/' in file and 'tests' not in file:
                matches.append(file)

    with open(outfilename, 'wb') as outfile:
        for filename in matches:
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)

    print(outfilename)


def prepair_for_cheating_detection(submissions_dir, project):
    target_dir = project.name
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    target_dir = os.path.abspath(target_dir)
    concat_java_projects(extract_files_to_dirs(submissions_dir), target_dir)
    files = [os.path.join(target_dir, f) for f in os.listdir(target_dir)]
    patoolib.create_archive(target_dir+'.zip', files)
