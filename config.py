import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = False
DROP_ENDPOINT = True
ENABLE_EMAIL_ACTIVATION = False
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


MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587,
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'evaluatorin@gmail.com'
MAIL_PASSWORD = ""