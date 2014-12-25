from flask.ext.restful import Resource, abort, marshal_with, marshal
from application import api, db
from application.models import Course, Project, Submission, Student
from decorators import student_required, login_required
from fields import submission_fields, project_fields
from flask import g, request
from werkzeug import secure_filename
from application.tasks import junit_task

class ProjectSubmissions(Resource):

    @student_required
    def post(self, course_name, name):
        """Creates a new submission."""
        course = Course.objects.get_or_404(name=course_name)
        project = Project.objects.get_or_404(name=name)
        if not project in course.projects:
            abort(404)
        if course.name != course_name:
            abort(404)       
        if len(request.files.values()) == 1:
            subm = Submission(submitter=g.user)
            for file in request.files.values():
                grid_file = db.GridFSProxy()
                grid_file.put(file, filename=secure_filename(file.filename))
                subm.code = grid_file
            subm.save()
            project.submissions.append(subm)
            project.save()
            junit_task.delay(str(subm.id))
            return marshal(subm.to_dict(), submission_fields), 201
        else:
            abort(400) # Bad request

    @login_required
    @marshal_with(submission_fields)
    def get(self, course_name, name):
        course = Course.objects.get_or_404(name=course_name)
        if isinstance(g.user, Student):
            for project in course.projects:
                if project.name == name:
                    return [subm for subm in project.submissions if subm.submitter == g.user]
            else:
                abort(404)
        else:
            return [project.submissions for project in course.projects if name == project.name]

class ProjectResource(Resource):
    @login_required
    @marshal_with(project_fields)
    def get(self, id):
        return Project.objects.get_or_404(id=id)

class ProjectsResource(Resource):
    @login_required
    @marshal_with(project_fields)
    def get(self, id):
        """
        All projects if teacher, only those registered for if student.
        """
        if isinstance(g.user, Student):
            courses = Course.objects(students=g.user)
            return [project for project in c.projects for c in courses]
        else:
            return [Project.objects.all()]

api.add_resource(ProjectSubmissions, '/course/<string:course_name>/projects/<string:name>/submissions',
                 endpoint='project_submissions_ep')

api.add_resource(
    ProjectResource, '/project/<string:id>', endpoint='project_ep')

