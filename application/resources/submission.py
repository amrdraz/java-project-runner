"""
Submission resource's endpoints.
"""
from application.models import Student, Submission
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
        if isinstance(g.user, Student) and g.user != subm.submitter:
            abort(403)
        else:
            return subm


api.add_resource(
    SingleSubmission, '/submission/<string:id>', endpoint='submission_ep')
