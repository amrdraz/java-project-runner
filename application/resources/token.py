"""
Defines Token resource's endpoints.
"""
import base64
from application import api
from application.models import User
from flask import request
from flask.ext.restful import Resource, abort


class TokenResource(Resource):
    """Token endpoints."""
    def post(self):
        """
        Post used even though no persistent entry is created
        since this is still creating a new resource,while granted 
        it only lives on the client side yet is still a new instance.
        """
        auth = request.headers.get('Authorization', None)
        if auth is not None:
            auth = auth.replace('Basic ', '', 1)
            try:
                auth = base64.b64decode(auth)
                values = auth.split(':')
                user = User.objects.get_or_404(email=values[0])
                if user.verify_pass(values[1]):
                    token = user.generate_auth_token()
                    return {"token": token}, 201
                else:
                    abort(401)
            except TypeError:
                # Wasn't a bse 64 string
                abort(400)
        else:
            abort(400)


api.add_resource(TokenResource, '/token', endpoint='token_ep')
