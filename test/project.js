var request = require('supertest');
var should = require('should');
var utils = require('./utils');


request = request(utils.host);


describe('Project', function() {

    // create fixtures of two teachers and two students
    // create a course whose only teacher is teacher_one
    var teacher_one = {
        name: 'Teacher One',
        email: 'teacher1.project@guc.edu.eg',
        password: 'pass'
    };
    var teacher_two = {
        name: 'Teacher Two',
        email: 'teacher2.project@guc.edu.eg',
        password: 'pass'
    };
    var student_one = {
        name: 'Student One',
        email: 'student1.project@student.guc.edu.eg',
        password: 'pass',
        guc_id: '22-1111'
    };

    var student_two = {
        name: 'Student Two',
        email: 'student2.project@student.guc.edu.eg',
        password: 'pass',
        guc_id: '22-1112'
    };
    var course = {
        name: 'CSEN 4XX',
        description: 'This is a very exciting course, people love it!'
    };

    before(function(done) {
        request.get(utils.drop_ep)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(200);
                done();
            });
    });


    before(function(done) {
        request.post(utils.users_ep)
            .send(teacher_one).end(function(err, res) {
                res.status.should.be.eql(201);
                teacher_one.id = res.body.id;
                teacher_one.url = res.body.url;
                done();
            });
    });

    before(function(done) {
        request.post(utils.users_ep)
            .send(teacher_two).end(function(err, res) {
                res.status.should.be.eql(201);
                teacher_two.id = res.body.id;
                teacher_two.url = res.body.url;
                done();
            });
    });

    before(function(done) {
        request.post(utils.users_ep)
            .send(student_one).end(function(err, res) {
                res.status.should.be.eql(201);
                student_one.id = res.body.id;
                student_one.url = res.body.url;
                done();
            });
    });

    before(function(done) {
        request.post(utils.users_ep)
            .send(student_two).end(function(err, res) {
                res.status.should.be.eql(201);
                student_two.id = res.body.id;
                student_two.url = res.body.url;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(teacher_one.email,
                    teacher_one.password))
            .end(function(err, res) {
                res.status.should.be.eql(201);
                teacher_one.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(teacher_two.email,
                    teacher_two.password))
            .end(function(err, res) {
                res.status.should.be.eql(201);
                teacher_two.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(student_one.email,
                    student_one.password))
            .end(function(err, res) {
                res.status.should.be.eql(201);
                student_one.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(student_two.email,
                    student_two.password))
            .end(function(err, res) {
                res.status.should.be.eql(201);
                student_two.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.courses_ep)
            .set('X-Auth-Token', teacher_one.token)
            .send(course)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                course = res.body;
                done();
            });
    });


    it('As a student I should not be able to create a new project', function(done) {

        dummy_project = {
            name: 'Foo Project',
            language: 'J'
        };

        request.post(course.projects_url)
            .set('X-Auth-Token', student_one.token)
            .field('name', dummy_project.name)
            .field('due_date', '2020-01-26T16:14:49Z' )
            .field('language', dummy_project.language)
            .attach('FooTest', 'test/fixtures/project_alpha/FooTest.java')
            .attach('BarTest', 'test/fixtures/project_alpha/BarTest.java')
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(403);
                done();
        });
    });

    it('As a student I should get a 404 on non existing project get', function(done) {
        request.get(utils.get_project_ep('8086'))
        .set('X-Auth-Token', student_one.token)
        .end(function(err, res) {
            should.not.exist(err);
            res.status.should.be.eql(404);
            done();
        });
    });

    it('As a teacher I should get a 404 on non existing project get', function(done) {
        request.get(utils.get_project_ep('8086'))
        .set('X-Auth-Token', teacher_one.token)
        .end(function(err, res) {
            should.not.exist(err);
            res.status.should.be.eql(404);
            done();
        });
    });

    it("As a teacher I should get a 404 for project submissions if project doesn't exist", function(done) {
        request.get(utils.get_project_subm_ep(course.name, 'dummy project'))
        .set('X-Auth-Token', teacher_one.token)
        .end(function(err, res) {
            should.not.exist(err);
            res.status.should.be.eql(404);
            done();
        });
    });

    it("As a student I should get a 404 for project submissions if project doesn't exist", function(done) {
        request.get(utils.get_project_subm_ep(course.name, 'dummy project'))
        .set('X-Auth-Token', student_one.token)
        .end(function(err, res) {
            should.not.exist(err);
            res.status.should.be.eql(404);
            done();
        });
    });


    it("As a teacher I should get a 404 for project submissions if course doesn't exist", function(done) {
        request.get(utils.get_project_subm_ep('ffffffff', 'dummy project'))
        .set('X-Auth-Token', teacher_one.token)
        .end(function(err, res) {
            should.not.exist(err);
            res.status.should.be.eql(404);
            done();
        });
    });

    it("As a student I should get a 404 for project submissions if course doesn't exist", function(done) {
        request.get(utils.get_project_subm_ep('ffffffff', 'dummy project'))
        .set('X-Auth-Token', student_one.token)
        .end(function(err, res) {
            should.not.exist(err);
            res.status.should.be.eql(404);
            done();
        });
    });

    describe('', function() {
        // project will be created by teacher_one
        project = {
            name: 'DMET 10XX',
            language: 'J'
        };

        before(function(done) {
            request.post(course.projects_url)
                .set('X-Auth-Token', teacher_one.token)
                .field('name', project.name)
                .field('language', project.language)
                .field('due_date', '2020-01-26T16:14:49Z' )
                .attach('FooTest', 'test/fixtures/project_alpha/FooTest.java')
                .attach('BarTest', 'test/fixtures/project_alpha/BarTest.java')
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(201);
                    project = res.body;
                    project.tests.should.be.an.instanceOf(Array)
                    .and.have.a.lengthOf(2);
                    done();
            });
        });

        it('As a teacher I can get a project by id', function(done) {
            request.get(project.url)
            .set('X-Auth-Token', teacher_one.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(200);
                res.body.should.have.properties({
                    name: project.name,
                    id: project.id,
                    language: project.language,
                    submissions_url: project.submissions_url
                });
                res.body.should.have.properties(['course', 'created_at']);
                done();
            });
        });

        it('As a student if I try to get a project by id that of a course that I am not a student of I should get a 403', function(done) {
            request.get(project.url)
            .set('X-Auth-Token', student_one.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(403);
                done();
            });
        });

        it('As a student if I try to get a project by id that of a course that I am not a teacher of I should get a 403', function(done) {
            request.get(project.url)
            .set('X-Auth-Token', student_two.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(403);
                done();
            });
        });

        it('As a teacher I can list all projects of courses that I teach', function(done) {
            request.get(utils.projects_ep)
            .set('X-Auth-Token', teacher_one.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(200);
                res.body.should.be.an.instanceOf(Array).
                and.have.a.lengthOf(1).
                and.matchEach(function(it) {
                    it.should.have.properties({
                        id: project.id,
                        name: project.name,
                        language: project.language,
                        created_at: project.created_at,
                        url: project.url
                    });
                });
                done();
            });
        });

        it('As a teacher I should only get the projects of courses that I teach', function(done) {
            request.get(utils.projects_ep)
            .set('X-Auth-Token', teacher_two.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(200);
                res.body.should.be.an.instanceOf(Array).
                and.have.a.lengthOf(0);
                done();
            });
        });

        it('As a teacher of a course I can list its projects', function(done) {
            request.get(course.projects_url)
            .set('X-Auth-Token', teacher_one.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(200);
                res.body.should.be.an.instanceOf(Array).
                and.have.a.lengthOf(1);
                done();
            });
        });

        it('As a teacher I get 403 if I list projects of a course I do not teach', function(done) {
            request.get(course.projects_url)
            .set('X-Auth-Token', teacher_two.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(403);
                done();
            });
        });
    });


}); // course describe