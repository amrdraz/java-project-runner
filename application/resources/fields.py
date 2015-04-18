"""
Marshaling fields
"""
from flask.ext.restful import fields

# User model fields
user_fields = {
    'email': fields.String,
    'name': fields.String,
    'guc_id': fields.String,
    'team_id': fields.String,
    'id': fields.String,
    'created_at': fields.DateTime('iso8601'),
    'active': fields.Boolean,
    'url': fields.Url(endpoint='user_ep')
}

token_fields = {
    'token': fields.String,
    'valid_for': fields.Integer,
    'user': fields.Nested(user_fields)
}

# Public course fields.
public_course_fields = {
    "name": fields.String,
    "description": fields.String,
    'created_at': fields.DateTime('iso8601'),
    "url": fields.Url(endpoint='course_ep')
}


course_fields = {
    "tas_url": fields.Url(endpoint='course_tas_ep'),
    "students_url": fields.Url(endpoint='course_students_ep'),
    "projects_url": fields.Url(endpoint='course_projects_ep'),
    "published": fields.String,
    "submissions_url": fields.Url(endpoint='course_submissions_ep'),
    "supervisor": fields.Nested(user_fields)

}

course_fields = dict(course_fields.items() + public_course_fields.items())


test_file_fields = {
    "name": fields.String,
    "download_url": fields.Url(endpoint='project_test_file_ep')
}

project_fields = {
    "id": fields.String,
    "name": fields.String,
    "course": fields.Nested(course_fields),
    "url": fields.Url(endpoint='project_ep'),
    "tests": fields.List(fields.Nested(test_file_fields)),
    'submissions_url': fields.Url(endpoint='project_submissions_ep'),
    'grades_url': fields.Url(endpoint='project_grades_ep'),
    'language': fields.String,
    'can_submit': fields.Boolean,
    'is_quiz': fields.String,
    'published': fields.String,
    'due_date': fields.DateTime('iso8601'),
    'created_at': fields.DateTime('iso8601')
}

test_case_fields = {
    "name": fields.String,
    "detail": fields.String,
    "passed": fields.Boolean,
    "error": fields.Boolean
}

test_result_fields = {
    "name": fields.String,
    "cases": fields.List(fields.Nested(test_case_fields)),
    "success": fields.Boolean,
    'created_at': fields.DateTime('iso8601')
}

submission_fields = {
    "id": fields.String,
    "url": fields.Url('submission_ep'),
    "submitter": fields.Nested(user_fields),
    "tests": fields.List(fields.Nested(test_result_fields)),
    "processed": fields.Boolean,
    "cases_count": fields.Integer,
    "passed_cases_count": fields.Integer,
    "passed_percentage": fields.Float,
    "project": fields.Nested(project_fields),
    'compiler_out': fields.String,
    'compile_status': fields.Boolean,
    'created_at': fields.DateTime('iso8601'),
    'download_url': fields.Url(endpoint='submission_download_ep')
}

team_project_grade_fields = {
    "id": fields.String,
    "team_id": fields.String,
    "project": fields.Nested(project_fields),
    "best_submission": fields.Nested(submission_fields)
}

# Pagination fields
page = {
    "page": fields.Integer,
    "pages": fields.Integer
}
submission_page_fields = dict(page, **{
    'submissions': fields.List(fields.Nested(submission_fields))
    })
user_page_fields = dict(page, **{
    'users': fields.List(fields.Nested(user_fields))
    })

public_course_page_fields = dict(page, **{
    'courses': fields.List(fields.Nested(public_course_fields))
    })

course_page_fields = dict(page, **{
    'courses': fields.List(fields.Nested(course_fields))
    })

team_project_grade_page_fields = dict(page, **{
    "grades": fields.List(fields.Nested(team_project_grade_fields))
    })
