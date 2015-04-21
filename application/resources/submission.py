"""
Submission resource's endpoints.
"""
from application.models import Student, Submission, Project
from application.tasks import junit_actual
from application import api
from decorators import login_required, student_required
from fields import submission_fields
from flask.ext.restful import Resource, marshal_with, abort
from flask import g, make_response


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
            course = proj.course
            if g.user in course.teachers:
                return subm.to_dict(parent_project=proj, parent_course=course)
            else:
                abort(403)

    @student_required
    def delete(self, id):
        """
        Deletes a submission, only it's submitter can delete it.
        """
        subm = Submission.objects.get_or_404(id=id)
        subm.code.delete()  # GridFS files must be deleted.
        if g.user == subm.submitter:
            subm.delete()
            return {}, 204
        else:
            abort(403)


class SingleSubmissionRun(Resource):

    @login_required
    @marshal_with(submission_fields)
    def get(self, id):
        """Rerun a single submission by id.
        Logged in user must be a teacher.
        """
        subm = Submission.objects.get_or_404(id=id)
        return subm.to_dict()


class SubmissionDownload(Resource):

    @login_required
    def get(self, id):
        subm = Submission.objects.get_or_404(id=id)
        proj = subm.project
        course = proj.course
        if g.user == subm.submitter or g.user in course.teachers:
            response = make_response(subm.code.read())
            response.headers['Content-Type'] = subm.code.content_type
            response.headers[
                'Content-Disposition'] = 'attachment; filename="{0}"'.format(subm.code.filename)
            return response
        else:
            abort(
                403, message="Only submitter or course teacher can download submission code.")

api.add_resource(SubmissionDownload, '/submission/<string:id>/download',
                 endpoint='submission_download_ep')
api.add_resource(
    SingleSubmission, '/submission/<string:id>', endpoint='submission_ep')
api.add_resource(
    SingleSubmissionRun, '/submission/<string:id>/run', endpoint='submission_run_ep')
