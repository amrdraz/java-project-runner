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
    def get(self):
        """
        Lists all submissions related to the course.
        """
        if isinstance(g.user, Student):
            return TeamProjectGrade.objects(team_id=g.user.team_id)
        else:
            abort(403, message="Must be a student to view grades")


class Foo(Resource):
    def get(self):
        return {'hello': 'world'}
    def post(self):
        return {'hello': 'world'}

api.add_resource(
    TeamProjectGrades, '/teamgrades', endpoint='team_project_grade_ep')

api.add_resource(
    Foo, '/testfoo', endpoint='test_grade_ep')
