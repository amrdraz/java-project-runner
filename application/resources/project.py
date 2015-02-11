from flask.ext.restful import Resource, abort, marshal_with, marshal
from application import api, db
from application.resources import allowed_test_file
from application.models import Course, Project, Submission, Student
from application.resources.decorators import student_required, login_required, teacher_required
from application.resources.fields import submission_fields, project_fields, submission_page_fields
from application.resources.pagination import custom_paginate_to_dict, paginate_iterable
from flask import g, request, make_response
from werkzeug import secure_filename
from application.tasks import junit_task
from application.resources import allowed_code_file
from application.resources.parsers import project_parser
import dateutil
from operator import attrgetter

class ProjectSubmissions(Resource):

    @student_required
    def post(self, course_name, name, page=1):
        """Creates a new submission."""
        try:
            course = Course.objects.get_or_404(name=course_name)
            project = Project.objects.get_or_404(name=name)
            if not g.user in course.students:
                abort(403, message="Must be a course student to submit")
            if not project in course.projects:
                abort(404, message="Project not found.")
            if not project.can_submit:
                abort(498, message="Due date hass passed, tough luck!")
            if len(request.files.values()) == 1:
                subm = Submission(submitter=g.user)
                for file in request.files.values():
                    if allowed_code_file(file.filename):
                        grid_file = db.GridFSProxy()
                        grid_file.put(
                            file, filename=secure_filename(file.filename), content_type=file.mimetype)
                        subm.code = grid_file
                    else:
                        abort(400, message="Only {0} files allowed".format(','.join(api.app.config['ALLOWED_CODE_EXTENSIONS'])))
                subm.save()
                project.submissions.append(subm)
                project.save()
                junit_task.delay(str(subm.id))
                return marshal(subm.to_dict(parent_course=course, parent_project=project), submission_fields), 201
            else:
                abort(400, message="Can only submit one file.")  # Bad request
        except Exception as e:
            abort(422, message=e.value)

    @login_required
    @marshal_with(submission_page_fields)
    def get(self, course_name, name, page=1):
        course = Course.objects.get_or_404(name=course_name)
        project = Project.objects.get_or_404(name=name)
        per_page = api.app.config['SUMBISSIONS_PAGE_SIZE']
        if isinstance(g.user, Student) and project.published:
            # Filter all submissions            
            subs = [sub for sub in project.submissions if g.user == sub.submitter]
            subs.sort(key=attrgetter('created_at'), reverse=True)
            # Paginate
            paginated = paginate_iterable(subs, page, per_page)
            # Convert to dicts for marshalling
            return custom_paginate_to_dict(paginated, 'submissions',
                page, len(subs), per_page, True,
                parent_course=course, parent_project=project)
        elif g.user in course.teachers:
            # No need to filter
            sorted_subs = sorted(project.submissions,
                key=attrgetter('created_at'), reverse=True)
            paginated = paginate_iterable(sorted_subs, page, per_page)
            return custom_paginate_to_dict(paginated, 'submissions',
                page, len(project.submissions), per_page, True,
                parent_course=course, parent_project=project)
        else:
            abort(403, message="You are not a student or course teacher.")  # not a student and not a course teacher


class ProjectResource(Resource):

    @login_required
    @marshal_with(project_fields)
    def get(self, id):
        """
        Returns a single project if g.user is a student in the parent course 
        or g.user is a teacher in parent course.
        return 500 if parent course not found.
        """
        proj = Project.objects.get_or_404(id=id)
        try:
            course = next(
                course for course in Course.objects if proj in course.projects)
            if g.user.can_view_project(proj, course):
                return proj.to_dict(parent_course=course)
            else:
                abort(403, message="Must be a course teacher or student to view project.")
        except StopIteration:
            abort(
                500, message="Found project with no parent course, Quick call an adult!")

    @teacher_required
    @marshal_with(project_fields)
    def put(self, id):
        """
        Modifies the due_data and test files fields.
        Test files are simply replaced.
        """
        proj = Project.objects.get_or_404(id=id)
        try:
            course = next(
                course for course in Course.objects if proj in course.projects)
            if g.user in course.teachers:
                args = project_parser.parse_args()
                if args['test_timeout'] != -1:
                    proj.test_timeout_seconds = args['test_timeout']
                if len(args['due_date']) > 0:
                    try:
                        due_date = args['due_date']
                        due_date = dateutil.parser.parse(due_date).astimezone(dateutil.tz.gettz('UTC')).replace(tzinfo=None)
                        proj.due_date = due_date
                    except:
                        abort(400, message="Incorrect due date format.")
                if len(request.files.values()) > 0:
                    filenames = [f.filename for f in request.files.values()]
                    if len(filenames) != len(set(filenames)):
                        abort(400, message="Test file names must be unique.")
                    for test in proj.tests:
                        test.delete()
                    proj.tests = []
                    proj.save()
                    for test_case in request.files.values():
                        if allowed_test_file(test_case.filename):
                            grid_file = db.GridFSProxy()
                            grid_file.put(
                                test_case, filename=secure_filename(test_case.filename), content_type=request.mimetype)
                            proj.tests.append(grid_file)
                        else:
                            abort(
                                400, message="{0} extension not allowed".format(test_case.filename))
            else:
                abort(403, message="Must be a course teacher to modify a project.")
            if args['published'] == 'True':
                proj.published = True
            elif args['published'] == 'False':
                proj.published == False
            proj.save()
        except StopIteration:
            abort(
                500, message="Found project with no parent course, Quick call an adult!")


class ProjectsResource(Resource):

    @login_required
    @marshal_with(project_fields)
    def get(self):
        """
        Projects of courses user teaches if teacher, only those registered for if student.
        """
        return [p.to_dict() for p in g.user.all_accessible_projects()]

class ProjectTestFileDownload(Resource):

    @teacher_required
    def get(self, project_id, name):
        project = Project.objects.get_or_404(id=project_id)
        course = Course.objects.get_or_404(projects=project)
        if g.user not in course.teachers:
            abort(403, message="Must be course teacher to view test files.")
        file = [f for f in project.tests if f.filename == name]
        if len(file) == 0:
            abort(404, message="File not found.")
        elif len(file) == 1:
            file = file[0]
            response = make_response(file.read())
            response.headers['Content-Type'] = file.content_type
            response.headers[
                'Content-Disposition'] = 'attachment; filename="{0}"'.format(file.filename)
            return response
        else:
            abort(500, message="More than one file found, server is confused.")


api.add_resource(
    ProjectTestFileDownload, '/project/<string:project_id>/tests/<string:name>', endpoint="project_test_file_ep")

api.add_resource(ProjectSubmissions, '/course/<string:course_name>/projects/<string:name>/submissions/<int:page>',
                 endpoint='project_submissions_ep')

api.add_resource(
    ProjectResource, '/project/<string:id>', endpoint='project_ep')

api.add_resource(ProjectsResource, '/projects', endpoint='projects_ep')
