from application import api, db
from flask import g, request, make_response
from werkzeug import secure_filename

from flask.ext.restful import Resource, abort, marshal_with, marshal
from application.models import (Course, Project, Submission, Student,
                                TeamProjectGrade)
from application.resources import allowed_test_file, allowed_code_file
from application.resources.decorators import (student_required, login_required,
                                              teacher_required)
from application.resources.fields import (submission_fields,
                                          project_fields,
                                          submission_page_fields,
                                          team_project_grade_fields,
                                          team_project_grade_page_fields)
from application.resources.pagination import mongo_paginate_to_dict
from application.resources.parsers import project_parser, submission_parser
from application.tasks import (junit_task, junit_no_deletion,
                               compute_team_grades)
import dateutil


class ProjectSubmissions(Resource):

    @student_required
    def post(self, course_name, name, page=1):
        """Creates a new submission."""
        course = Course.objects.get_or_404(name=course_name)
        project = Project.objects.get_or_404(name=name)
        if len(Submission.objects(project=project, submitter=g.user, processed=False)) > 4:
            abort(429, message="Too many pending submissions") 
        if not g.user in course.students:
            abort(403, message="Must be a course student to submit")
        if not project in course.projects:
            abort(404, message="Project not found.")
        if not project.can_submit:
            abort(498, message="Due date has passed, tough luck!")
        if project.is_quiz:
            # Verify verification code
            args = submission_parser.parse_args()
            if g.user.verification_code != args['verification_code']:
                abort(400, message="Invalid verification code.")
                

        if len(request.files.values()) == 1:
            subm = Submission(submitter=g.user, project=project)
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
            if api.app.config['DELETE_SUBMISSIONS']:
                junit_task.delay(str(subm.id))
            else:
                junit_no_deletion.delay(str(subm.id))
            return marshal(subm.to_dict(parent_course=course, parent_project=project), submission_fields), 201
        else:
            abort(400, message="Can only submit one file.")  # Bad request

    @login_required
    @marshal_with(submission_page_fields)
    def get(self, course_name, name, page=1):
        try:
            course = Course.objects.get(name=course_name)
        except:
            abort(404, message="Course not found")
        try:
           project = Project.objects.get(name=name, course=course)
        except: 
            abort(404, message="Project not found")
        per_page = api.app.config['SUMBISSIONS_PAGE_SIZE']
        if isinstance(g.user, Student) and project.published:
            # Filter all submissions            
            subs = Submission.objects(submitter=g.user,
                project=project).order_by('-created_at').paginate(page,
                per_page)
            return mongo_paginate_to_dict(subs, 'submissions')
        elif g.user in course.teachers:
            # No need to filter
            subs = Submission.objects(project=project).order_by('-created_at').paginate(page, per_page)
            return mongo_paginate_to_dict(subs, 'submissions')
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
            old_tests = []
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
                    old_tests = proj.tests
                    proj.tests = []
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
                proj.published = False
            if args['is_quiz'] == 'True':
                proj.is_quiz = True
            elif args['is_quiz'] == 'False':
                proj.is_quiz = False
            if len(old_tests) != 0:
                for test in old_tests:
                    test.delete()
            proj.save()
            return proj.to_dict()
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
        course = project.course
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

class ProjectGrades(Resource):
    @login_required
    def get(self, project_id, page=1, rerurn_submissions=False):
        """
        Retrieves all grades or single student grade.
        """
        project = Project.get_or_404(project_id)
        if isinstance(g.user, Student):
            return marshal(
                TeamProjectGrade.objects(project=project,
                                         team_id=g.user.team_id),
                team_project_grade_fields)
        else:
            if g.user not in project.course.teachers:
                abort(403, message="Must be course teacher to view grades")
            pages = (TeamProjectGrade.objects(project=project)
                     .paginate(page,
                               api.app.config['PROJECT_TEAM_GRADES_PER_PAGE']))
            return marshal(mongo_paginate_to_dict(pages, "grades"),
                           team_project_grade_page_fields)

    @teacher_required
    def post(self, project_id, page=1, rerurn_submissions="no"):
        """
        Computes grade.
        """
        project = Project.objects.get_or_404(id=project_id)
        course = project.course
        if g.user not in course.teachers:
            abort(403, message="Must be course teacher to compute grades.")
        if not project.can_submit:
            abort(422, message="Can only compute grades when we are past the deadline.")
        rerurn_submissions_bool = rerurn_submissions == "yes"
        compute_team_grades.delay(str(project.id), rerurn_submissions_bool)



api.add_resource(
    ProjectTestFileDownload,
    '/project/<string:project_id>/tests/<string:name>',
    endpoint="project_test_file_ep")

api.add_resource(ProjectSubmissions,
                 '/course/<string:course_name>/projects/<string:name>/submissions/<int:page>',
                 endpoint='project_submissions_ep')

api.add_resource(ProjectGrades,
                 '/project/<string:id>/grades/<string:rerurn_submissions>/<int:page>',
                 endpoint='project_grades_ep')

api.add_resource(
    ProjectResource, '/project/<string:id>', endpoint='project_ep')

api.add_resource(ProjectsResource, '/projects', endpoint='projects_ep')
