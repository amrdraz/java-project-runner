"""
Defines Token resource's endpoints.
"""
import base64
from application import api, app
from application.models import User
from flask import request
from flask.ext.restful import Resource, abort, marshal
from fields import token_fields
from application.models import Student
from parsers import token_parser


class TokenResource(Resource):
    """Token endpoints."""
    def post(self):
        """
        Post used even though no persistent entry is created
        since this is still creating a new resource,while granted 
        it only lives on the client side yet is still a new instance.
        """
        auth = request.headers.get('X-Auth', None)
        if auth is not None:
            auth = auth.replace('Basic ', '', 1)
            try:
                auth = base64.b64decode(auth)
                values = auth.split(':')
                if len(values) != 2:
                    abort(400, message="Malformed X-Auth Header.")
                user = User.objects(email=values[0])
                if len(user) != 1:
                    abort(401, message='Invalid email or password')
                else:
                    user = user[0]
                if app.config['ENABLE_EMAIL_ACTIVATION'] and not user.active:
                    abort(422, message='Inactive user')
                if user.verify_pass(values[1]):
                    remember = token_parser.parse_args()['remember']
                    duration = 12 * 30 * 24 * 60 * 60 if remember == 'true' else  10 * 60
                    token = user.generate_auth_token(duration)
                    return marshal({"token": token, "valid_for": duration, "user": user.to_dict()}, token_fields), 201
                else:
                    abort(401, message='Invalid email or password')
            except TypeError:
                # Wasn't a base 64 string
                abort(400, message="Not a base 64 string")
        else:
            abort(400, message="Missing X-Auth field")


api.add_resource(TokenResource, '/token', endpoint='token_ep')
