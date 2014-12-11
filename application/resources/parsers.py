from flask.ext.restful import reqparse



# User parser
user_parser = reqparse.RequestParser()
user_parser.add_argument('email', str)
user_parser.add_argument('password', str)
user_parser.add_argument('guc_id', str)
