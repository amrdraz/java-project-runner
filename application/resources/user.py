from application import api, db
from application.models import User, Student
from flask.ext.restful import Resource, abort, marshal, marshal_with, fields
from parsers import user_parser
from decorators import login_required
from flask import g

# User model marshalling
user_fields = {
    'email': fields.String,
    'name': fields.String,
    'guc_id': fields.String,
    'id': fields.String,
    'created_at': fields.DateTime('iso8601'),
    'url': fields.Url(endpoint='user_ep')
}


class UsersResource(Resource):

    """User collection"""

    def post(self):
        arguments = user_parser.parse_args()
        guc_id = arguments['guc_id']
        password = arguments['password']
        email = arguments['email']
        name = arguments['name']
        if guc_id is not None:
            user = Student(guc_id=guc_id, email=email, name=name)
        else:
            user = User(email=email, name=name)
        user.password = password
        try:
            user.save()
            return marshal(user.to_dict(), user_fields), 201
        except db.ValidationError:
            abort(422, message='Invalid field values')
        except db.NotUniqueError:
            abort(422, message='Email already in use')


class UserResource(Resource):

    """Singular resource"""
    method_decorators = [login_required]

    @marshal_with(user_fields)
    def put(self, id):
        if g.id == id:
            arguments = user_parser.parse_args()
            args = {
                "set__{0}".format(key): val for key, val in arguments.items()
                if val is not None and key != "email" and key != "password"
            }
            if len(args) > 0:
                g.user.update(**args)
            if arguments['password'] is not None:
                g.user.password = arguments['password']
            g.user.save()
            return g.user.to_dict()
        else:
            abort(401)

    @marshal_with(user_fields)
    def get(self, id):
        return g.user.to_dict()

    def delete(self, id):
        g.user.delete()
        return {}, 204

api.add_resource(UsersResource, '/users', endpoint='users_ep')
api.add_resource(UserResource, '/user/<string:id>', endpoint='user_ep')
