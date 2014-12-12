import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True


MONGODB_SETTINGS = {
'DB': "project_runner"
}

SECRET_KEY = "123?"

ALLOWED_EXTENSIONS = ['zip', 'tar', 'gz', 'bz', 'rar', '7z', 'java']
