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
                if g.user is not None:
                    return f(*args, **kwargs)
                else:
                    abort(401)
            except (BadSignature, SignatureExpired):
                abort(401)
        else:
            abort(401)
    return decorator
