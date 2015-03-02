"""Defines Course related endpoints."""
from application import api, db
from application.models import Course, Student, Project, User
from application.resources import allowed_test_file
from application.resources.parsers import course_parser, project_parser, user_parser
from application.resources.decorators import login_required, login_mutable, teacher_required
from flask import g, request
from flask.ext.restful import Resource, abort, marshal_with, marshal
from application.resources.fields import (course_fields, public_course_fields,
    project_fields, user_fields, submission_page_fields, user_page_fields,
    course_page_fields, public_course_page_fields)
from application.resources.pagination import paginate_iterable, custom_paginate_to_dict, mongo_paginate_to_dict
from werkzeug import secure_filename
import dateutil
import itertools

# Primary Course resources


class CoursesResource(Resource):

    """Courses Collection."""
    @teacher_required
    def post(self, page=1):
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
        if arguments['published'] == 'True':
            course.published = True
        elif arguments['published'] == 'False':
            course.published = False
        else:
            abort(400, message="published field must be True or False as a string.")
        try:
            course.save()
            return marshal(course.to_dict(), course_fields), 201
        except db.NotUniqueError:
            abort(422, message='Course name already in use.')

    @login_mutable
    def get(self, page=1):
        """
        Lists all courses.
        Must be logged in.
        """
        per_page = api.app.config['COURSE_PAGE_SIZE']
        if g.user is None:
            model_fields = public_course_page_fields
            paginated_courses = Course.objects(published=True).paginate(page, per_page)
            pages = mongo_paginate_to_dict(paginated_courses, 'courses')
        else:
            model_fields = course_page_fields
            courses = g.user.all_accessible_courses()
            paginated_courses = paginate_iterable(courses, page, per_page)
            pages = custom_paginate_to_dict(paginated_courses, "courses", page,
                len(courses), per_page, True)
        return marshal(pages, model_fields)


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
        if not g.user.can_view_course(course):
            abort(403, message="You can not view this course. It is probably not ready for you!")
        return marshal(course.to_dict(), model_fields), 200

# Course related resources


class CourseSubmissions(Resource):
    method_decorators = [teacher_required, marshal_with(submission_page_fields)]

    def get(self, name, page=1):
        """
        Lists all submissions related to the course.
        """
        course = Course.objects.get_or_404(name=name)
        per_page = api.app.config['SUMBISSIONS_PAGE_SIZE']
        if not g.user.can_view_course(course):
            abort(403, message='message must be a course teacher to view all submissions')
        all_submissions = itertools.imap(lambda proj: proj.submissions, course.projects)
        flat_submissions = itertools.chain.from_iterable(all_submissions)
        all_submissions = paginate_iterable(flat_submissions, page, per_page)

        return custom_paginate_to_dict(all_submissions, 'submissions',
                page, len(all_submissions), per_page, True,
                parent_course=course)


class CourseTeachers(Resource):

    @login_required
    @marshal_with(user_page_fields)
    def get(self, name, page=1):
        """
        Lists the course's TAs.
        Must be logged in to access the list.
        """
        course = Course.objects.get_or_404(name=name)
        per_page = api.app.config['TA_PAGE_SIZE']
        paginated = paginate_iterable(course.teachers, page, per_page)
        return custom_paginate_to_dict(paginated, 'users', page, len(course.teachers), per_page, True)

    @teacher_required
    def post(self, name, page=1):
        """
        Adds a teacher to the course.
        Logged in user must be a teacher.
        """
        course = Course.objects.get_or_404(name=name)
        teacher = User.objects.get_or_404(id=user_parser.parse_args()['id'])
        if not isinstance(teacher, Student):
            if not (g.user.id == teacher.id or g.user in course.teachers):
                # I can add myself or I can be added by existing course staff
                abort(403, message='Can only add self, or must be a course teacher to add others.')
            if teacher in course.teachers:
                abort(422, message='Already a course teacher.')
            course.teachers.append(teacher)
            course.save()
            return {}, 204
        else:
            abort(400, message="Can not add student as a course teacher.")

    @teacher_required
    def delete(self, name, page=1):
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
                abort(404, message="Not a course teacher.")
        else:
            abort(403, message='Must be a course teacher')


class CourseStudents(Resource):
    method_decorators = [login_required]

    def post(self, name, page=1):
        """
        Adds a student to the course.
        Logged in user must be student to be added or a course teacher
        """
        student = User.objects.get_or_404(id=user_parser.parse_args()['id'])
        if isinstance(student, Student):
            course = Course.objects.get_or_404(name=name)
            if g.user in course.teachers or g.user.id == student.id:
                if student in course.students:
                    abort(422, message='Student already registered for course.')
                course.students.append(student)
                course.save()
                return {}, 204
            else:
                abort(403, message='Can only add self as student or be added by a course teacher.')
        else:
            abort(400, message='Can not add a teacher as a course student.')  # Terrible request

    @marshal_with(user_page_fields)
    def get(self, name, page=1):
        """
        Lists the course's student.
        Must be logged in to access the list.
        """
        course = Course.objects.get_or_404(name=name)
        per_page = api.app.config['STUDENT_PAGE_SIZE']
        paginated = paginate_iterable(course.students, page, per_page)
        return custom_paginate_to_dict(paginated, 'users', page, len(course.students), per_page, True)

    def delete(self, name, page=1):
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
            abort(403, message='Can only unregister self.')


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
            return [project.to_dict(parent_course=course) for project in course.projects if g.user.can_view_project(project, course)]
        else:
            abort(403,  message='Must be course teacher or student to view projects')
          

    @teacher_required
    def post(self, name):
        """
        Creates a new project for this course.
        User must be a course Teacher.
        """
        course = Course.objects.get_or_404(name=name)
        if g.user not in course.teachers:
            abort(403, message='Must be course teacher to add a project.')
        args = project_parser.parse_args()
        name = args['name']
        language = args['language']
        due_date = args['due_date']
        if due_date is None or due_date == '':
            abort(400, message="Project must have due date.")
        try:
            due_date = dateutil.parser.parse(due_date).astimezone(dateutil.tz.gettz('UTC')).replace(tzinfo=None)
        except:
            abort(400, message="Incorrect due date format.")
        if len([p for p in course.projects if p.name == name]) != 0:
            abort(422, message="Request makes no sense, grab a programmer.")
        filenames = [f.filename for f in request.files.values()]
        if len(filenames) != len(set(filenames)):
            abort(400, message="Test file names must be unique.")
        project = Project(name=name, language=language, due_date=due_date, course=course)
        if args['test_timeout'] != -1:
            project.test_timeout_seconds = args['test_timeout']
        for test_case in request.files.values():
            if allowed_test_file(test_case.filename):
                grid_file = db.GridFSProxy()
                grid_file.put(
                    test_case, filename=secure_filename(test_case.filename), content_type=request.mimetype)
                project.tests.append(grid_file)
            else:
                abort(
                    400, message="{0} extension not allowed".format(test_case.filename))
        if args['published'] == 'True':
            project.published = True
        elif args['published'] == 'False':
            project.published = False
        else:
            abort(400, message="published value must be True or False as string.")
        project.save()
        course.projects.append(project)
        course.save()
        return marshal(project.to_dict(parent_course=course), project_fields), 201


api.add_resource(CourseProjects, '/course/<string:name>/projects',
                 endpoint='course_projects_ep')
api.add_resource(CoursesResource, '/courses/<int:page>', endpoint='courses_ep')
api.add_resource(CourseResource, '/course/<string:name>', endpoint='course_ep')
api.add_resource(CourseStudents, '/course/<string:name>/students/<int:page>',
                 endpoint='course_students_ep')
api.add_resource(CourseTeachers, '/course/<string:name>/tas/<int:page>',
                 endpoint='course_tas_ep')
api.add_resource(CourseSubmissions, '/course/<string:name>/submissions/<int:page>',
                 endpoint='course_submissions_ep')
