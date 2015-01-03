"""Defines Course related endpoints."""
from application import api, db
from application.models import Course, Student, Project, User
from application.resources import allowed_test_file
from parsers import course_parser, project_parser, user_parser
from decorators import login_required, login_mutable, teacher_required
from flask import g, request
from flask.ext.restful import Resource, abort, marshal_with, marshal
from fields import course_fields, public_course_fields, project_fields, user_fields, submission_fields
from werkzeug import secure_filename
import itertools

# Primary Course resources


class CoursesResource(Resource):

    """Courses Collection."""
    @teacher_required
    def post(self):
        """
        Creates a new course, 
        current user is set as supervisor.
        aborts with code 403 if current user is a Student.
        """
        arguments = course_parser.parse_args()
        name = arguments['name']
        description = arguments.get('description', '')
        course = Course(
            name=name, description=description, supervisor=g.user)
        course.teachers.append(g.user)
        try:
            course.save()
            return marshal(course.to_dict(), course_fields), 201
        except db.NotUniqueError:
            abort(422, message='Course name already in use.')

    @login_mutable
    def get(self):
        """
        Lists all courses.
        Must be logged in.
        """
        if g.user is None:
            model_fields = public_course_fields
        else:
            model_fields = course_fields
        return marshal([course.to_dict() for course in Course.objects], model_fields)


class CourseResource(Resource):

    """Singular course resource"""
    @login_mutable
    def get(self, name):
        """Displays information of a course to both guests and logged in users.
        only public information is displayed to guests
        """
        if g.user is None:
            model_fields = public_course_fields
        else:
            model_fields = course_fields
        course = Course.objects.get_or_404(name=name)
        return marshal(course.to_dict(), model_fields), 200

# Course related resources


class CourseSubmissions(Resource):
    method_decorators = [teacher_required, marshal_with(submission_fields)]

    def get(self, name):
        """
        Lists all submissions related to the course.
        """
        course = Course.objects.get_or_404(name=name)
        if g.user not in course.teachers:
            abort(403)
        submissions = []
        for project in course.projects:
            submissions = map(lambda subm: subm.to_dict(parent_project=project, parent_course=course),
                                         itertools.chain(submissions, project.submissions))
        return submissions


class CourseTeachers(Resource):

    @login_required
    @marshal_with(user_fields)
    def get(self, name):
        """
        Lists the course's TAs.
        Must be logged in to access the list.
        """
        course = Course.objects.get_or_404(name=name)
        return [teacher.to_dict() for teacher in course.teachers]

    @teacher_required
    def post(self, name):
        """
        Adds a teacher to the course.
        Logged in user must be a teacher.
        """
        course = Course.objects.get_or_404(name=name)
        teacher = User.objects.get_or_404(id=user_parser.parse_args()['id'])
        if not isinstance(teacher, Student):
            if not (g.user.id == teacher.id or g.user in course.teachers):
                # I can add myself or I can be added by existing course staff
                abort(403)
            if teacher in course.teachers:
                abort(422)
            course.teachers.append(teacher)
            course.save()
            return {}, 204
        else:
            abort(400, message="can not add student as a teacher")

    @teacher_required
    def delete(self, name):
        """
        Removes a teacher from the course.
        Logged in user must be a course teacher.
        """
        course = Course.objects.get_or_404(name=name)
        if g.user in course.teachers:
            teacher = User.objects.get_or_404(
                id=user_parser.parse_args()['id'])
            if teacher in course.teachers:
                course.teachers.remove(teacher)
                course.save()
                return {}, 204
            else:
                abort(404)
        else:
            abort(403, message='Must be a course teacher')


class CourseStudents(Resource):
    method_decorators = [login_required]

    def post(self, name):
        """
        Adds a student to the course.
        Logged in user must be student to be added or a course teacher
        """
        student = User.objects.get_or_404(id=user_parser.parse_args()['id'])
        if isinstance(student, Student):
            course = Course.objects.get_or_404(name=name)
            if g.user in course.teachers or g.user.id == student.id:
                if student in course.students:
                    abort(422)
                course.students.append(student)
                course.save()
                return {}, 204
            else:
                abort(403)
        else:
            abort(400)  # Terrible request

    @marshal_with(user_fields)
    def get(self, name):
        """
        Lists the course's student.
        Must be logged in to access the list.
        """
        course = Course.objects.get_or_404(name=name)
        return [student.to_dict() for student in course.students]

    def delete(self, name):
        """
        Removes a student from the course.
        Logged in user must be a course teacher or the student in question.
        """
        course = Course.objects.get_or_404(name=name)
        student = Student.objects.get_or_404(id=user_parser.parse_args()['id'])
        if student in course.students and (g.user == student or g.user in course.teachers):
            course.students.remove(student)
            course.save()
            return {}, 204
        else:
            abort(403)


class CourseProjects(Resource):

    """Course projects as collection"""

    @login_required
    @marshal_with(project_fields)
    def get(self, name):
        """
        Lists course projects.
        name is parent course name
        returns 403 if not a course teacher or student.
        """
        course = Course.objects.get_or_404(name=name)
        if g.user in course.students or g.user in course.teachers:
            return [project.to_dict(parent_course=course) for project in course.projects]
        else:
            abort(403)
          

    @teacher_required
    def post(self, name):
        """
        Creates a new project for this course.
        User must be a course Teacher.
        """
        course = Course.objects.get_or_404(name=name)
        if g.user not in course.teachers:
            abort(403)
        args = project_parser.parse_args()
        name = args['name']
        language = args['language']
        if len([p for p in course.projects if p.name == name]) != 0:
            abort(422)
        project = Project(name=name, language=language)
        for test_case in request.files.values():
            if allowed_test_file(test_case.filename):
                grid_file = db.GridFSProxy()
                grid_file.put(
                    test_case, filename=secure_filename(test_case.filename))
                project.tests.append(grid_file)
            else:
                abort(
                    400, message="{0} extension not allowed".format(test_case.filename))
        project.save()
        course.projects.append(project)
        course.save()
        return marshal(project.to_dict(parent_course=course), project_fields), 201


api.add_resource(CourseProjects, '/course/<string:name>/projects',
                 endpoint='course_projects_ep')
api.add_resource(CoursesResource, '/courses', endpoint='courses_ep')
api.add_resource(CourseResource, '/course/<string:name>', endpoint='course_ep')
api.add_resource(CourseStudents, '/course/<string:name>/students',
                 endpoint='course_students_ep')
api.add_resource(CourseTeachers, '/course/<string:name>/tas',
                 endpoint='course_tas_ep')
api.add_resource(CourseSubmissions, '/course/<string:name>/submissions',
                 endpoint='course_submissions_ep')
