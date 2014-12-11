"""
Document definitions.
"""
from application import db, app
from flask.ext.bcrypt import generate_password_hash, check_password_hash
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature


class User(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    email = db.EmailField(required=True, unique=True)
    name = db.StringField(max_length=512, required=True)
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
        seriliezer = TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'], expires_in=expires_in)
        return seriliezer.dumps({'id': str(self.id)})

    @staticmethod
    def verify_auth_token(token):
        s = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.objects.get(id=data['id'])
        return user

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "email": self.email,
            "password": self.password,
            "name": self.name
        }


class Student(User):
    guc_id = db.StringField(max_length=32, required=True)

    def to_dict(self):
        dic = User.to_dict(self)
        dic['guc_id'] = self.guc_id
        return dic


class Course(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    projects = db.ListField(db.EmbeddedDocumentField('Project'))
    teacher = db.ListField(
        db.ReferenceField('User', reverse_delete_rule=db.PULL))
    students = db.ListField(
        db.ReferenceField('Student', reverse_delete_rule=db.PULL))


class Project(db.EmbeddedDocument):

    """A course's Project."""
    LANGUAGES = [('J', 'Java Project')]
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=256, unique=True, required=True)
    tests = db.ListField(db.FileField())
    language = db.StringField(max_length=3, choices=LANGUAGES, required=True)
    submissions = db.ListField(db.EmbeddedDocumentField('Submission'))


class TestCase(db.EmbeddedDocument):

    """Single case of a TestResult."""
    name = db.StringField(max_length=512, required=True)
    detail = db.StringField(max_length=512, required=True)
    passed = db.BooleanField(default=False, required=True)


class TestResult(db.EmbeddedDocument):

    """Results for a single test ran on a submission."""
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    name = db.StringField(max_length=256, required=True)
    cases = db.ListField(db.EmbeddedDocumentField('TestCase'))
    success = db.BooleanField(default=False, required=True)


class Submission(db.EmbeddedDocument):

    """A student's submission."""
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    test_results = db.ListField(db.EmbeddedDocumentField('TestResult'))
    processed = db.BooleanField(default=False, required=True)
    submitter = db.ReferenceField('Student', required=True)
