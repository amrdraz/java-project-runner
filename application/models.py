"""
Document definitions.
"""
from application import db, app
from flask.ext.bcrypt import generate_password_hash, check_password_hash
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer, URLSafeSerializer, SignatureExpired, BadSignature, URLSafeTimedSerializer


class User(db.DynamicDocument):

    """Base document for all users."""
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    email = db.StringField(
        max_length=256, min_length=1, required=True, unique=True)
    name = db.StringField(max_length=512, min_length=1, required=True)
    password_hash = db.StringField(max_length=60, required=True)
    active = db.BooleanField(default=False, required=True)
    activation_sent_at = db.DateTimeField()
    reset_sent_at = db.DateTimeField()
    meta = {'allow_inheritance': True,
            "indexes": [
                {
                    "fields": ['email'],
                    "unique": True
                },
                {
                    "fields": ['name']
                }
            ]
            }

    @property
    def is_student(self):
        return False
    @property
    def is_teacher(self):
        return not self.is_student

    def all_accessible_projects(self):
        return [p for p in self.all_accessible_courses if self.can_view_project(p)]

    def all_accessible_courses(self):
        return [c for c in Course.objects if self.can_view_course(c)]

    def can_view_course(self, course):
        """Checks if the user has authorization to view a course."""
        return (self.is_teacher or (self.is_student and course.published))

    def can_view_submission(self, submission, project, course):
        return (self.can_view_project(project, course) and 
            (self.is_teacher or (submission.submitter == self)))

    def can_view_project(self, project, course):
        """Checks if the user has authorization to view a project."""
        return (course.is_user_associated(self) and 
            (self.is_teacher) or
            (self in course.students and project.published))


    @property
    def password(self):
        """Returns password hash, not actual password."""
        return self.password_hash

    @password.setter
    def password(self, value):
        """Hashes password."""
        self.password_hash = generate_password_hash(value, 12)

    def send_activation_mail(self):
        """Updates sent_at time and schedules a task."""
        from application.tasks import activation_mail_task
        self.activation_sent_at = datetime.datetime.utcnow()
        self.save()
        activation_mail_task.delay(str(self.id))

    def send_password_reset_mail(self):
        """Updates reset_sent_at time and schedules a task."""
        from application.tasks import password_reset_mail_task
        self.reset_sent_at = datetime.datetime.utcnow()
        self.save()
        password_reset_mail_task.delay(str(self.id))

    def reset_pass(self):
        from application.tasks import send_random_password
        send_random_password.delay(str(self.id))

    def generate_pass_reset_token(self):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], expires_in=app.config['PASS_RESET_EXPIRATION'])
        return serializer.dumps({'id': str(self.id), 'email': self.email, 'type': 'reset_pass'})

    @staticmethod
    def verify_pass_reset_token(token):
        """
        Retrieves user who is identified by this token.
        Raises SignatureExpired, BadSignature if expired or malformed.
        """
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        data = serializer.loads(token)
        matches = User.objects(id=data[id])
        if matches.count() != 1 or matches[0].email != data['email'] or data['type'] != 'reset_pass':
            raise BadSignature("Could not verify password reset token")
        return matches[0]

    def verify_pass(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in):
        """Creates an expiring token to uniquely identify this user."""
        seriliezer = TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'], expires_in=expires_in)
        return seriliezer.dumps({'id': str(self.id)})

    def generate_activation_token(self):
        """
        Creates a token to uniquely identify this user.
        Token is URL safe.
        """
        seriliezer = URLSafeSerializer(app.config['SECRET_KEY'])
        self.activation_sent_at = datetime.datetime.utcnow()
        return seriliezer.dumps({'email': self.email})

    @staticmethod
    def verify_activation_token(token):
        """
        Retrieves user who is identified by this token.
        Raises BadSignature if bad token.
        """
        serializer = URLSafeSerializer(app.config['SECRET_KEY'])
        data = serializer.loads(token)
        matches = User.objects(email=data['email'])
        if matches.count() != 1:
            raise BadSignature("Could not identify owner.")
        return matches[0]

    @staticmethod
    def verify_auth_token(token):
        """
        Retrieves user who is identified by this token.
        Raises SignatureExpired, BadSignature if expired or malformed.
        """
        s = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        data = s.loads(token)
        matches = User.objects(id=data['id'])
        if matches.count() != 1:
            raise BadSignature("Could not identify owner.")
        return matches[0]

    def to_dict(self, **kwargs):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "active": self.active
        }


class Student(User):
    guc_id = db.StringField(max_length=32, min_length=2, required=True)
    @property
    def is_student(self):
        return True
    def to_dict(self, **kwargs):
        dic = User.to_dict(self)
        dic['guc_id'] = self.guc_id
        return dic


class Course(db.Document):
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    projects = db.ListField(db.ReferenceField('Project'))
    name = db.StringField(
        max_length=256, min_length=4, unique=True, required=True)
    description = db.StringField(max_length=1024, min_length=10, required=True)
    supervisor = db.ReferenceField('User', reverse_delete_rule=db.PULL)
    teachers = db.ListField(
        db.ReferenceField('User', reverse_delete_rule=db.PULL))
    students = db.ListField(
        db.ReferenceField('Student', reverse_delete_rule=db.PULL))
    published = db.BooleanField(default=True)

    def is_user_associated(self, user):
        """Checks if user in course students or teachers."""
        return user in self.students or user in self.teachers

    meta = {
        "indexes": [
            {
                "fields": ['name'],
                "unique": True
            }
        ]
    }

    def to_dict(self, **kwargs):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "published": self.published,
            "supervisor": self.supervisor.to_dict(),
            'page': 1
        }


class Project(db.Document):

    """A course's Project."""
    LANGUAGES = [('J', 'Java Project')]
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    due_date = db.DateTimeField(required=True)
    name = db.StringField(max_length=256, min_length=5, required=True)
    tests = db.ListField(db.FileField())
    published = db.BooleanField(default=True, required=True)
    language = db.StringField(
        max_length=3, min_length=1, choices=LANGUAGES, required=True)
    test_timeout_seconds = db.LongField(
        default=600, max_value=1800, required=True)
    submissions = db.ListField(db.ReferenceField('Submission'))

    @property
    def has_tests(self):
        return len(tests) >= 1

    @property
    def can_submit(self):
        return self.due_date >= datetime.datetime.utcnow()

    def to_dict(self, **kwargs):
        parent_course = kwargs.get('parent_course', None)
        dic = {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "created_at": self.created_at,
            "course": (parent_course.to_dict(**kwargs) if parent_course is not None
                       else Course.objects.get(projects=self).to_dict(**kwargs)),
            "can_submit": self.can_submit,
            "due_date": self.due_date,
            'published': self.published,
            'page': 1
        }
        dic['course_name'] = dic['course']['name']

        def file_to_dic(project_id, file):
            dic = {
                "name": file.filename,
                "mimetype": file.content_type,
                "project_id": project_id
            }
            return dic
        dic['tests'] = [file_to_dic(self.id, f) for f in self.tests]
        return dic


class TestCase(db.EmbeddedDocument):

    """Single case of a TestResult."""
    name = db.StringField(max_length=512, min_length=1, required=True)
    detail = db.StringField(max_length=512, required=True)
    error = db.BooleanField(default=False, required=True)
    passed = db.BooleanField(default=False, required=True)

    def to_dict(self, **kwargs):
        return {
            "name": self.name,
            "detail": self.detail,
            "error": self.error,
            "passed": self.passed
        }


class TestResult(db.EmbeddedDocument):

    """Results for a single test ran on a submission."""
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    name = db.StringField(max_length=256, min_length=1, required=True)
    cases = db.ListField(db.EmbeddedDocumentField('TestCase'))
    success = db.BooleanField(default=False, required=True)

    def to_dict(self, **kwargs):
        return {
            "name": self.name,
            "created_at": self.created_at,
            "cases": [case.to_dict() for case in self.cases],
            "success": self.success
        }


class Submission(db.Document):

    """A student's submission."""
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    test_results = db.ListField(db.EmbeddedDocumentField('TestResult'))
    processed = db.BooleanField(default=False, required=True)
    submitter = db.ReferenceField('Student', required=True)
    code = db.FileField(required=True)
    compile_status = db.BooleanField(default=False, required=True)
    compiler_out = db.StringField(max_length=8086)

    def to_dict(self, **kwargs):
        parent_project = kwargs.get('parent_project', None)
        dic = {
            "id": self.id,
            "created_at": self.created_at,
            "processed": self.processed,
            "submitter": self.submitter.to_dict(),
            "tests": [test.to_dict() for test in self.test_results],
            "project": (parent_project.to_dict(**kwargs) if parent_project is not None
                        else Project.objects.get(submissions=self).to_dict(**kwargs)),
            'compile_status': self.compile_status,
            'compiler_out': self.compiler_out
        }
        dic['project_name'] = dic['project']['name']
        dic['course_name'] = dic['project']['course_name']
        return dic
