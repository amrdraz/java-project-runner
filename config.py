import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
DROP_ENDPOINT = True
ENABLE_EMAIL_ACTIVATION = True
MAIL_FAIL_SILENTLY = True
MONGODB_SETTINGS = {
    'DB': "project_runner"
}

CELERY_BROKER_URL = 'amqp://localhost'

SECRET_KEY = "123?"
PASS_RESET_EXPIRATION = 60 * 60 # in seconds
ALLOWED_CODE_EXTENSIONS = ['zip', 'tar', 'gz', 'bz', 'rar', '7z']
ALLOWED_TEST_EXTENSIONS = ['java']
# 512 Mi
MAX_CONTENT_LENGTH = 512 * (2 ** 20)

# In bytes
FILE_BUFFER_SIZE = os.stat('.').st_blksize

ANT_BUILD_FILE_NAME = 'build.xml'
ANT_TESTS_DIR_NAME = 'tests'
ANT_BUILD_DIR_NAME = 'build'
ANT_RUN_FILE_NAME = 'ant_script.sh'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CLEAN_TEMP_DIRS = True

SUMBISSIONS_PAGE_SIZE = 10
STUDENT_PAGE_SIZE = 5
TA_PAGE_SIZE  = 5
COURSE_PAGE_SIZE = 5
SEARCH_RESULTS_PER_PAGE = 10
PROJECT_TEAM_GRADES_PER_PAGE = 10

DEFAULT_MAIL_SENDER='no-reply@evaluator.in'

DELETE_SUBMISSIONS = False
