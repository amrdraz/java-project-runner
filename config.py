import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = False
DROP_ENDPOINT = True

MONGODB_SETTINGS = {
'DB': "project_runner"
}

CELERY_BROKER_URL = 'amqp://localhost'

SECRET_KEY = "123?"

ALLOWED_EXTENSIONS = ['zip', 'tar', 'gz', 'bz', 'rar', '7z', 'java']

# In bytes
FILE_BUFFER_SIZE = os.stat('.').st_blksize

ANT_BUILD_FILE_NAME = 'build.xml'
ANT_TESTS_DIR_NAME = 'tests'
ANT_BUILD_DIR_NAME = 'build'
ANT_RUN_FILE_NAME = 'ant_script.sh'