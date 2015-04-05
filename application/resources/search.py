"""
Search endpoints.
"""
from application import api, db, app
from flask.ext.restful import Resource, abort, marshal_with
from application.models import Student, Submission, Project
from application.resources.decorators import teacher_required
from application.resources.parsers import search_parser
from application.resources.pagination import mongo_paginate_to_dict
from application.resources.fields import submission_page_fields


class SubmissionSearch(Resource):

    @teacher_required
    @marshal_with(submission_page_fields)
    def post(self):
        per_page = app.config['SEARCH_RESULTS_PER_PAGE']
        args = search_parser.parse_args()
        args = dict([(key, value)
                     for (key, value) in args.items() if key is not None])
        if 'page' not in args:
            abort(400, message="must specify page")
        if not any(
                key in args for key in
                ['student_id', 'team_id', 'project_id']):
            abort(400, message="must have at least one query field")
        students = Student.objects(
            db.Q(team_id=args.get('team_id'))
            | db.Q(guc_id=args.get('guc_id')))
        if 'project_id' in args:
            if len(students) > 0:
                subs = (Submission.objects(submitter__in=students,
                                           project=Project.objects(
                                            id=args['project_id']))
                        .order_by('-created_at')
                        .paginate(args['page'], per_page))
            else:
                subs = (Submission.objects(
                    project=Project.objects(id=args['project_id']))
                        .order_by('-created_at')
                        .paginate(args['page'], per_page))
        else:
            subs = Submission.objects(submitter__in=students).order_by(
                '-created_at').paginate(args['page'], per_page)
        return mongo_paginate_to_dict(subs, 'submissions')


api.add_resource(
    SubmissionSearch, '/search/submissions', endpoint='submission_search')
