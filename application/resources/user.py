from application import api, db
from application.models import User, Student, Teacher
from flask.ext.restful import Resource, abort, marshal, marshal_with, fields
from parsers import user_parser


user_fields = {
    'email': fields.String,
    'guc_id': fields.String,
    'id': fields.String,
    'created_at': fields.DateTime('iso8601'),
    'url': fields.Url('user_ep')
}

class UsersResource(Resource):
    def post(self):
        arguments = user_parser.parse_args()
        guc_id = arguments['guc_id']
        password = arguments['password']
        email = arguments['email']
        if guc_id is not None:
            user = Student(guc_id=guc_id, email=email)
        else:
            user = Teacher(email=email)
        user.password = password
        try:
            user.save()
            return marshal(user, user_fields), 201
        except db.ValidationError:
            abort(422, message='Invalid field values')
        except db.NotUniqueError:
            abort(422, message='Email already in use')


class UserResource(Resource):
    @marshal_with(user_fields)
    def put(self, id):
        arguments = user_parser.parse_args()
        args = {
            "set__{0}".format(key): val for key, val in arguments.items()
            if val is not None and key != "email" and key != "password"
        }
        user = User.objects.get_or_404(id=id)
        if len(args) > 0:
            user.update(**args)
        if arguments['password'] is not None:
            user.password = arguments['password']
        user.save()
        return user

    @marshal_with(user_fields)
    def get(self, id):
        return User.objects.get_or_404(id=id)

    def delete(self, id):
        User.object(id=id).delete()
        return {}, 204

api.add_resource(UsersResource, '/users', endpoint='users_ep')
api.add_resource(UserResource, '/user/<string:id>', endpoint='user_ep')    
