"""
Defines User resource's endpoints.
"""
from application import api, db
from application.models import User, Student
from flask.ext.restful import Resource, abort, marshal, marshal_with
from fields import user_fields
from parsers import user_parser
from decorators import login_required
from flask import g



class UsersResource(Resource):

    """User collection."""

    def post(self):
        """
        Creates a new user.
        Decides if teacher based on email host name.
        """
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
        except db.NotUniqueError:
            abort(422, message='Email already in use.')


class UserResource(Resource):

    """Singular resource."""
    method_decorators = [login_required]

    @marshal_with(user_fields)
    def put(self, id):
        """
        Updates the fields of the resource.
        email updates are not allowed, but will not trigger a fail. Instead
        they are silently ignored.
        """
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
        """
        Returns a single user.
        While a login is required, No special user privileges are given to 
        specific users. As there is no private data in the profiles that isn't 
        shared anyway amongst TAs and Students. 
        """
        return User.objects.get(id=id).to_dict()

    def delete(self, id):
        """
        Deletes the currently logged in user.
        Redundant id parameter is to be consistent with REST conventions 
        or just not to stray too much from the middle.
        """
        g.user.delete()
        return {}, 204

api.add_resource(UsersResource, '/users', endpoint='users_ep')
api.add_resource(UserResource, '/user/<string:id>', endpoint='user_ep')
