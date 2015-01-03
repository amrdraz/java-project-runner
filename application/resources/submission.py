"""
Submission resource's endpoints.
"""
from application.models import Student, Submission, Project, Course
from application import api
from decorators import login_required
from fields import submission_fields
from flask.ext.restful import Resource, marshal_with, abort
from flask import g


class SingleSubmission(Resource):

    @login_required
    @marshal_with(submission_fields)
    def get(self, id):
        """Returns a single submission by id.
        Logged in user must be submitter or a teacher.
        """
        subm = Submission.objects.get_or_404(id=id)
        if isinstance(g.user, Student):
            if g.user == subm.submitter:
                return subm.to_dict()
            else:
                abort(403)
        else:
            proj = Project.objects.get_or_404(submissions=subm)
            course = Course.objects.get_or_404(projects=proj)
            if g.user in course.teachers:
                return subm.to_dict(parent_project=proj, parent_course=course)
            else:
                abort(403)


api.add_resource(
    SingleSubmission, '/submission/<string:id>', endpoint='submission_ep')
