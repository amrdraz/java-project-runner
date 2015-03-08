"""
Defines various request parsers for our resources.
In order to cover all methods of a resource with a single parser
arguments that are not found and silently set to None.
"""
from flask.ext.restful import reqparse



# User parser
user_parser = reqparse.RequestParser()
user_parser.add_argument('email', str)
user_parser.add_argument('password', str)
user_parser.add_argument('guc_id', str)
user_parser.add_argument('name', str)
user_parser.add_argument('id', str)

# Course Parser
course_parser = reqparse.RequestParser()
course_parser.add_argument('name', str)
course_parser.add_argument('description', str)
course_parser.add_argument('published', str)

# project parser
project_parser = reqparse.RequestParser()
project_parser.add_argument('name', str)
project_parser.add_argument('language', str)
project_parser.add_argument('due_date', str)
project_parser.add_argument('published', str)
project_parser.add_argument('is_quiz', str)
project_parser.add_argument('test_timeout', default=-1, type=int)
# submission parser
submission_parser = reqparse.RequestParser()
submission_parser.add_argument('verification_code', str)
# token parser
token_parser = reqparse.RequestParser()
token_parser.add_argument('remember', str)