from flask import g, request
from functools import wraps
from flask.ext.restful import abort
from application.models import User, BadSignature, SignatureExpired


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('X-Auth-Token', None)
        if token is not None:
            try:
                g.user = User.verify_auth_token(token)
                return f(*args, **kwargs)
            except (BadSignature, SignatureExpired):
                abort(401)
        else:
            abort(401)
