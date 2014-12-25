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

# project parser
project_parser = reqparse.RequestParser()
project_parser.add_argument('name', str)
project_parser.add_argument('language', str)

# submission parser