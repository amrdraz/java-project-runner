var request = require('supertest');
var should = require('should');
var utils = require('./utils');


request = request(utils.host);

describe('Submission', function() {
    // Create Fixtures
    course = {
        name: "Submission Test Course",
        description: "A Course, for sumbitting!"
    };

    teacher = {
        name: "Hello, I am a teacher!",
        email: 'teacher@guc.edu.eg',
        password: 'pass'
    };

    student = {
        name: 'Hello, I am a student!',
        email: 'someone@student.guc.edu.eg',
        password: 'pass',
        guc_id: '16-4477'
    };

    project = {
        name: 'Foo Project',
        language: 'J'
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
            .send(student)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                student = res.body;
                done();
            });
    });


    before(function(done) {
        request.post(utils.users_ep)
            .send(teacher)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                teacher = res.body;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('Authorization',
                utils.auth_header_value(student.email,
                    'pass'))
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                student.token = res.body.token;
                done();
            });
    });
    before(function(done) {
        request.post(utils.token_ep)
            .set('Authorization',
                utils.auth_header_value(teacher.email,
                    'pass'))
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                teacher.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.courses_ep)
            .set('X-Auth-Token', teacher.token)
            .send(course)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                course = res.body;
                done();
            });
    });

    before(function(done) {
        request.post(course.projects_url)
            .field('name', project.name)
            .field('language', project.language)
            .set('X-Auth-Token', teacher.token)
            .attach('FooTest', 'test/fixtures/project_alpha/FooTest.java')
            .attach('BarTest', 'test/fixtures/project_alpha/BarTest.java')
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                project = res.body;
                done();
            });
    });

    before(function(done) {
        request.post(course.students_url)
            .set('X-Auth-Token', student.token)
            .send({
                id: student.id
            })
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(204);
                done();
            });
    });
    subm = {};
    it('As a student I can submit a submission', function(done) {
        request.post(project.submissions_url)
            .attach('subm', 'test/fixtures/project_alpha/src.zip')
            .set('X-Auth-Token', student.token)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                subm = res.body;
                done();
            });
    });

    describe('List submissions', function() {
        before(function(done) {
            request.post(project.submissions_url)
                .attach('subm', 'test/fixtures/project_alpha/src.zip')
                .set('X-Auth-Token', student.token)
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(201);
                    subm = res.body;
                    done();
                });
        });

        it('As a teacher I can list all submissions of a course', function(done) {
            request.get(course.submissions_url)
                .set('X-Auth-Token', teacher.token)
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(200);
                    res.body.should.be.an.instanceOf(Array);
                    done();
                });
        })
    });
});