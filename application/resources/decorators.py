"""
Defines decorators for use with resource methods.
Currently provides Authorization logic.
"""
from application.models import User, BadSignature, SignatureExpired, Student
from flask import g, request
from flask.ext.restful import abort
from werkzeug.exceptions import Unauthorized
from functools import wraps

def login_required(f):
    """
    Sets g.current user to logged in User instance
    prior to calling f. Calls abort with 401 status if can not verify
    credentials or expired token.
    """
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


def login_mutable(f):
    """g.user is None to represent annon."""
    login_bind = login_required(f)
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            return login_bind(*args, **kwargs)
        except Unauthorized:
            g.user = None
            return f(*args, **kwargs)
    return decorator

def teacher_required(f):
    """Logged in user must be a teacher."""
    @wraps(f)
    @login_required
    def decorator(*args, **kwargs):
        if not isinstance(g.user, Student):
            return f(*args, **kwargs)
        else:
            abort(403, message='Must be teacher to perform action.')
    return decorator

