"""
Submission resource's endpoints.
"""
from application.models import Student, Submission, Project, Course, TeamProjectGrade
from application import api
from decorators import login_required, student_required
from fields import team_project_grade_fields
from flask.ext.restful import Resource, marshal_with, abort
from flask import g, make_response


class TeamProjectGrades(Resource):

    @login_required
    @marshal_with(team_project_grade_fields)
    def get(self, id):
        """
        Lists all submissions related to the course.
        """
        if isinstance(g.user, Student):
            return TeamProjectGrade.objects(team_id=g.user.team_id)
        else:
            abort(403, message="Must be a student to view grades")

api.add_resource(
    TeamProjectGrades, '/teamgrades/', endpoint='team_project_grade_ep')
