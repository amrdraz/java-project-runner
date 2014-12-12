from flask.ext.restful import Resource, abort, marshal_with
from application import api
from application.models import Course, Project, Submission, Student
from decorators import student_required, login_required
from fields import submission_fields, project_fields
from flask import g, request


class ProjectSubmissions(Resource):

    @student_required
    def post(self, course_name, name):
        """Creates a new submission."""
        course = Course.objects.get_or_404(name=course_name)
        if course.name != course_name:
            abort(404)
        if request.mimetype in ['application/x-gzip', 'application/x-tar', 'application/zip', 'application/x-7z-compressed', 'application/x-rar-compressed', 'application/x-bzip2']:
            grid_file = db.GridFSProxy()
            grid_file.put(request.data)
            sub = Submission(submitter=g.user)
            sub.code = grid_file
            sub.save()
            projs = [
                project for project in course.projects if project.name == name]
            if 0 == len(projs):
                abort(404)
            elif len(projs) > 1:
                abort(500)
            else:
                proj = projs[0]
                proj.submissions.append(sub)
                proj.save()
                return marshal_with(sub, submission_fields), 204
        else:
            abort(400)

    @login_required
    @marshal_with(submission_fields)
    def get(self, course_name, name):
        course = Course.objects.get_or_404(name=course_name)
        if isinstance(g.user, Student):
            for project in course.projects:
                if project.name == name:
                    for subm in project.submissions:
                        if subm.submitter == g.user:
                            return subm
            else:
                return []
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
                 endpoint='project_submission_ep')

api.add_resource(
    ProjectResource, '/project/<string:id>', endpoint='project_ep')

