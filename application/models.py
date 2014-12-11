"""
Document definitions.
"""
from application import db, app
from flask.ext.bcrypt import generate_password_hash, check_password_hash
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature

class User(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    email = db.EmailField(required=True)
    password_hash = db.StringField(max_length=60, required=True)

    meta = {'allow_inheritance': True}

    @property
    def password(self):
        """Returns password hash, not actual password."""
        return self.password_hash
    @password.setter
    def password(self, value):
        """Hashes password."""
        self.password_hash = generate_password_hash(value, 12)

    def verify_pass(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        seriliezer = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'], expires_in=expires_in)
        return seriliezer.dumps({'id': str(self.id)})

    @staticmethod
    def verify_auth_token(token):
        s = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.objects.get(id=data['id'])
        return user


class Student(User):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    guc_id = db.StringField(max_length=32, required=True)

class Teacher(User):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    

