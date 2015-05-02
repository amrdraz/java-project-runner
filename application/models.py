"""
Document definitions.
"""
from __future__ import division
from application import db, app
from flask.ext.bcrypt import generate_password_hash, check_password_hash
import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer, URLSafeSerializer,
                          SignatureExpired, BadSignature,
                          URLSafeTimedSerializer)


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
                },
                {
                    "fields": ['password_hash']
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
        return [p for p in
                self.all_accessible_courses if self.can_view_project(p)]

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
        """Changes password and sends new one via email"""
        from application.tasks import send_random_password
        send_random_password.delay(str(self.id))

    def generate_pass_reset_token(self):
        """Sends a password reset email."""
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(
            {'id': str(self.id), 'email': self.email, 'type': 'reset_pass'})

    @staticmethod
    def verify_pass_reset_token(token):
        """
        Retrieves user who is identified by this token.
        Raises SignatureExpired, BadSignature if expired or malformed.
        """
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        data = serializer.loads(token,
                                max_age=app.config['PASS_RESET_EXPIRATION'])
        matches = User.objects(id=data['id'])
        if (matches.count() != 1 or matches[0].email != data['email']
                or data['type'] != 'reset_pass'):
            raise BadSignature("Could not verify password reset token")
        return matches[0]

    def verify_pass(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in):
        """Creates an expiring token to uniquely identify this user."""
        seriliezer = TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'], expires_in=expires_in)
        return seriliezer.dumps(
            {'id': str(self.id), 'salty_hash': self.password_hash})

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
        if 'id' not in data or 'salty_hash' not in data:
            raise BadSignature('Invalid Token')
        matches = User.objects(id=data['id'], password_hash=data['salty_hash'])
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
            "active": self.active,
            'page': 1
        }


class Student(User):
    team_id = db.StringField(max_length=32, min_length=1, required=False)
    guc_id = db.StringField(max_length=32, min_length=2, required=True)
    major = db.StringField(max_length=32, min_length=2, required=False)
    tutorial = db.StringField(max_length=32, min_length=2, required=False)
    verification_code = db.StringField()

    @property
    def is_student(self):
        return True

    @property
    def team_grades(self):
        return TeamProjectGrade.objects(team_id=self.team_id) if self.team_id else []

    def to_dict(self, **kwargs):
        dic = User.to_dict(self)
        dic['guc_id'] = self.guc_id
        dic['team_id'] = self.team_id
        dic['major'] = self.major
        dic['tutorial'] = self.tutorial
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
    published = db.BooleanField(default=True, required=True)

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




class TestCase(db.Document):

    """Single case of a TestResult."""
    name = db.StringField(min_length=1, required=True)
    detail = db.StringField(required=True)
    error = db.BooleanField(default=False, required=True)
    passed = db.BooleanField(default=False, required=True)

    def to_dict(self, **kwargs):
        return {
            "name": self.name,
            "detail": self.detail,
            "error": self.error,
            "passed": self.passed
        }


class TestResult(db.Document):

    """Results for a single test ran on a submission."""
    created_at = db.DateTimeField(
        default=datetime.datetime.utcnow, required=True)
    name = db.StringField(min_length=1, required=True)
    cases = db.ListField(
        db.ReferenceField('TestCase', reverse_delete_rule=db.PULL))
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
    test_results = db.ListField(
        db.ReferenceField('TestResult', reverse_delete_rule=db.PULL))
    processed = db.BooleanField(default=False, required=True)
    submitter = db.ReferenceField('Student', required=True,
                                  reverse_delete_rule=db.CASCADE)
    project = db.ReferenceField('Project', required=True)
    code = db.FileField(required=True)
    compile_status = db.BooleanField(default=False, required=True)
    compiler_out = db.StringField()
    started_processing_at = db.DateTimeField()
    finished_processing_at = db.DateTimeField()

    meta = {
        "indexes": [
            {
                "fields": ['submitter']
            },
            {
               "fields": ['project']
            }
        ]
    }

    def reset(self):
        """
        Resets status as if never processed.
        Note: Saves document.
        """
        self.processed = False
        self.compile_status = False
        self.compiler_out = None
        self.started_processing_at = None
        self.finished_processing_at = None
        for result in list(self.test_results):
            for case in list(result.cases):
                case.delete()
            result.delete()
        self.test_results = []
        self.save()

    @property
    def processing_duration(self):
        return self.finished_processing_at - self.started_processing_at

    @property
    def cases_count(self):
        return reduce(lambda c,x:c+len(x.cases),self.test_results, 0)

    @property
    def passed_cases_count(self):
        return reduce(lambda c,x:c+reduce(lambda c,y: c+1 if y.passed else c, x.cases, 0),self.test_results, 0)

    @property
    def passed_percentage(self):
        return (self.passed_cases_count/self.cases_count)*100 if self.cases_count>0 else 0

    def to_dict(self, **kwargs):
        dic = {
            "id": self.id,
            "created_at": self.created_at,
            "processed": self.processed,
            "submitter": self.submitter.to_dict(),
            "tests": [test.to_dict() for test in self.test_results],
            "project": self.project.to_dict(),
            'compile_status': self.compile_status,
            'compiler_out': self.compiler_out,
            "cases_count": self.cases_count,
            "passed_cases_count": self.passed_cases_count,
            "passed_percentage": self.passed_percentage,
        }
        dic['project_name'] = dic['project']['name']
        dic['course_name'] = dic['project']['course_name']
        dic['grade'] = dic['project']['course_name']
        return dic


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
    submissions = db.ListField(
        db.ReferenceField('Submission', reverse_delete_rule=db.PULL))
    course = db.ReferenceField('Course')
    is_quiz = db.BooleanField(required=True)

    meta = {
        "indexes": [
            {
                "fields": ['name']
            },
            {
                "fields": ['course']
            }
        ]
    }

    @property
    def has_tests(self):
        return len(self.tests) >= 1

    @property
    def has_class_files(self):
        return any([t.filename.endswith('.class') for t in self.tests])

    @property
    def can_submit(self):
        return self.due_date >= datetime.datetime.utcnow()

    def student_results_for_csv(self):
        grades = TeamProjectGrade.objects(project=self)
        results = []
        for grade in grades:
            for student in grade.get_students():
                results.append({
                    "team_id": student.team_id,
                    "guc_id": student.guc_id,
                    "name": student.name,
                    "email": student.email,
                    "project": self.name,
                    "passed cases": grade.best_submission.passed_cases_count,
                    "total cases": grade.best_submission.cases_count,
                    "grade in percentage": grade.grade,
                    "submitter": grade.best_submission.submitter.name
                })
        return results

    def get_teams_canadite_submissions(self):
        """
        Gets teams candidate submissions for grading.
        Gets latest submission of each member of a team.
        returns a list of (team_id, submissions)
        """
        from itertools import groupby
        from operator import attrgetter
        key_func = attrgetter('team_id')
        submitters = sorted([subm.submitter for subm in Submission.objects(project=self, submitter__exists=True)],
                            key=key_func)
        submissions = []
        for _, team in groupby(submitters, key_func):
            if _ is None:
                continue
            team = list(set(list(team)))
            canadite_submissions = []
            for student in team:
                subms = (Submission.objects(
                            submitter=student,
                            project=self)
                         .order_by('-created_at').limit(1))
                if len(subms) > 0:
                    canadite_submissions.append(subms[0])

            submissions.append((_, canadite_submissions))
        return submissions

    def get_team_best_submissions(
            self,
            rerurn_submissions=False,
            only_rerun_compile_error=False,
            get_latest=True):
        """
        Cget team best submissions for grades, optionally reruns submissions.
        Please note that this function will block to submissions.
        returns a list of (team_id, submission)
        """
        from application.tasks import junit_actual
        canadite_submissions = self.get_teams_canadite_submissions()
        best_team_submissions = []
        if get_latest:
            for _, submissions in canadite_submissions:
                submissions = sorted(submissions,
                                     key=lambda subm:
                                     subm.created_at, reverse=True)
                submission = submissions[0]
                if rerurn_submissions:
                    if only_rerun_compile_error and submission.compile_status:
                        pass
                    else:
                        submission.reset()
                        junit_actual(submission.id)
                best_team_submissions.append((_, submission))
        else:
            for _, submissions in canadite_submissions:
                if rerurn_submissions:
                    for submission in submissions:
                        if only_rerun_compile_error\
                           and submission.compile_status:
                            continue
                        else:
                            submission.reset()
                            junit_actual(submission.id)
                passed_submissions = [s for s in canadite_submissions
                                      if s.compile_status]
                best_submissions = sorted(passed_submissions,
                                          key=lambda subm: len(
                                            subm.test_results))
                best_team_submissions.append((_, best_submissions[0]))
        return best_team_submissions

    def grade_teams(
            self,
            rerurn_submissions=False,
            only_rerun_compile_error=False,
            get_latest=True):
        """
        Computes team grades, optionally reruns submissions.
        Please note that this function will block to submissions.
        will attempt to find TeamGrade and update it if it already exists
        """

        best_team_submissions = self.get_team_best_submissions(
            rerurn_submissions, only_rerun_compile_error, get_latest)

        for team_id, best_submission in best_team_submissions:
            try:
                grade = TeamProjectGrade.objects.get(
                    team_id=team_id, project=self)
                if not rerurn_submissions:
                    app.logger.info("found grade nothing to change")
                    continue
                else:
                    app.logger.info("found grade updateing submission")
                    grade.best_submission = best_submission
            except TeamProjectGrade.DoesNotExist:
                grade = TeamProjectGrade(
                    team_id=team_id,
                    best_submission=best_submission,
                    project=self)
            grade.save()
            app.logger.info("graded team {0} in project {1}"
                            .format(team_id, self.name))

    def get_student_submissions(
            self,
            rerurn_submissions=False,
            only_rerun_compile_error=False,
            only_rerun_test_cases_zero=False,
            get_latest=True):
        """
        Computes latest grade for each student who submitted in this project, optionally reruns submissions.
        Please note that this function will block to submissions.
        will attempt to find TeamGrade and update it if it already exists
        """
        from application.tasks import junit_actual

        students = self.course.students
        submissions = []
        for student in students:
            subms = (Submission.objects(
                        submitter=student,
                        project=self)
                     .order_by('-created_at').limit(1))
            if len(subms) > 0:
                submissions.append(subms[0])

        for submission in submissions:
            if rerurn_submissions:
                if only_rerun_compile_error and submission.compile_status:
                    pass
                elif only_rerun_test_cases_zero and submission.cases_count > 0:
                    pass
                else:
                    submission.reset()
                    junit_actual(submission.id)

        return submissions

    def student_submissions_for_csv(self):

        results = []
        for submission in self.get_student_submissions():
            student = submission.submitter
            results.append({
                "guc_id": student.guc_id,
                "name": student.name,
                "email": student.email,
                "project": self.name,
                "passed cases": submission.passed_cases_count,
                "total cases": submission.cases_count,
                "grade in percentage": submission.passed_percentage,
            })
        return results


    def to_dict(self, **kwargs):
        dic = {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "created_at": self.created_at,
            "course": self.course.to_dict(),
            "can_submit": self.can_submit,
            "due_date": self.due_date,
            'published': self.published,
            "is_quiz": self.is_quiz,
            "rerurn_submissions": "no",
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
        dic['has_class_files'] = self.has_class_files
        return dic


class TeamProjectGrade(db.Document):
    """
    Team based grades.
    """

    team_id = db.StringField(max_length=32, min_length=1, required=False)
    best_submission = db.ReferenceField('Submission',
                                        reverse_delete_rule=db.CASCADE)
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)

    meta = {
        "indexes": [
            {
                "fields": ['team_id'],
            },
            {
               "fields": ['project']
            },
            {
                "fields": ['project', 'team_id'],
                "unique": True
            }
        ]
    }

    @property
    def grade(self):
        return self.best_submission.passed_percentage

    @property
    def submitter(self):
        return self.best_submission.submitter

    def get_students(self):
        return list(Student.objects(team_id=self.team_id))

    def to_dict(self, **kwargs):

        return {
            "id": self.id,
            "team_id": self.team_id,
            "best_submission": self.best_submission.to_dict(),
            "project": self.project.to_dict(),
            "page": 1
        }


class StudentQuizGrade(db.Document):
    """
    Team Quiz grades.
    """

    passed_tests = db.FloatField(required=False)
    total_tests = db.FloatField(required=False)
    grade_in_percentage = db.FloatField(required=False)

    quiz = db.StringField(max_length=32, min_length=1, required=False)
    student = db.ReferenceField('Student', reverse_delete_rule=db.CASCADE)

    meta = {
        "indexes": [
            {
                "fields": ['quiz'],
            },
            {
               "fields": ['student']
            },
            {
                "fields": ['student', 'quiz'],
                "unique": True
            }
        ]
    }

    def to_dict(self, **kwargs):

        return {
            "id": self.id,
            "passed_tests": self.passed_tests,
            "total_tests": self.total_tests,
            "grade_in_percentage": self.grade_in_percentage,
            "quiz": self.quiz,
            "student": self.student.to_dict(),
            "page": 1
        }


class StudentMilestoneGrade(db.Document):
    """
    Team Quiz grades.
    """

    milestone_ratio = db.FloatField(required=False)
    grade_in_percentage = db.FloatField(required=False)

    milestone = db.StringField(max_length=32, min_length=1, required=False)
    student = db.ReferenceField('Student', reverse_delete_rule=db.CASCADE)

    meta = {
        "indexes": [
            {
                "fields": ['milestone'],
            },
            {
               "fields": ['student']
            },
            {
                "fields": ['student', 'milestone'],
                "unique": True
            }
        ]
    }

    def to_dict(self, **kwargs):

        return {
            "id": self.id,
            "milestone_ratio": self.milestone_ratio,
            "grade_in_percentage": self.grade_in_percentage,
            "milestone": self.milestone,
            "student": self.student.to_dict(),
            "page": 1
        }


class StudentProjectCode(db.Document):
    """
    Quiz codes for students.
    """
    student = db.ReferenceField('Student',
                                reverse_delete_rule=db.CASCADE, required=True)
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE, required=True)
    verification_code = db.StringField(required=True)
    meta = {
        "indexes": [
            {
                "fields": ['student', 'project'],
                "unique": True
            },
            {
                "fields": ['verification_code']
            }
        ]
    }

    def to_dict(self):
        return {
            "id": self.id,
            "student": self.student.to_dict(),
            "project": self.project.to_dict(),
            "verification_code": self.verification_code
        }
