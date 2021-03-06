"""
Package containing resource endpoints (views) and related utility functionality.
This package should always reflect the api.md document in the api branch.
Any issues should be filed as API related and reflected in the api branch 
before executed here.
"""
from application import app, api
from flask.ext import restful



def allowed_code_file(filename):
    """Returns true if file with name filename is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_CODE_EXTENSIONS']

def allowed_test_file(filename):
    """Returns true if file with name filename is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_TEST_EXTENSIONS']

def allowed_class_file(filename):
    """Returns true if file with name filename is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_TEST_EXTENSIONS']

class ClearDB(restful.Resource):
    def get(self):
        from application.models import Project, User, Student, Course, Submission
        Submission.objects.delete()
        Project.objects.delete()
        Course.objects.delete()
        Student.objects.delete()
        User.objects.delete()
        return {}, 200


if app.config['DROP_ENDPOINT']:
    api.add_resource(ClearDB, '/drop', endpoint='drop_db_ep')
