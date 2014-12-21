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
from flanker.addresslib import address


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
        parsed_email = address.parse(email)
        if parsed_email is None or not parsed_email.hostname.endswith('guc.edu.eg'):
            abort(400)
        if User.objects(email=email).count() != 0:
            abort(422) # Duplicate found
        if parsed_email.hostname.startswith('student'):
            user = Student(guc_id=guc_id, email=email, name=name)
        else:
            user = User(email=email, name=name)
        user.password = password
        user.save()
        return marshal(user.to_dict(), user_fields), 201

    @marshal_with(user_fields)
    @login_required
    def get(self):
        return [user.to_dict() for user in User.objects]

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
        if str(g.user.id) == id:
            arguments = user_parser.parse_args()
            if "guc_id" in arguments and arguments['guc_id'] != '' and not isinstance(g, Student):
                abort(400)
            args = {
                "set__{0}".format(key): val for key, val in arguments.items()
                if val is not None and val != '' and key != "email" and key != "password"
            }
            if len(args) > 0:
                g.user.update(**args)
            if arguments['password'] is not None and arguments['password'] != '':
                g.user.password = arguments['password']
            g.user.save()
            return g.user.to_dict()
        else:
            abort(403)

    @marshal_with(user_fields)
    def get(self, id):
        """
        Returns a single user.
        While a login is required, No special user privileges are given to 
        specific users. As there is no private data in the profiles that isn't 
        shared anyway amongst TAs and Students. 
        """
        return User.objects.get_or_404(id=id).to_dict()

    def delete(self, id):
        """
        Deletes the currently logged in user.
        Redundant id parameter is to be consistent with REST conventions 
        or just not to stray too much from the middle.
        """
        if str(g.user.id) == id:
            g.user.delete()
            return {}, 204
        else:
            abort(400)

api.add_resource(UsersResource, '/users', endpoint='users_ep')
api.add_resource(UserResource, '/user/<string:id>', endpoint='user_ep')
