var request = require('supertest');
var should = require('should');
var utils = require('./utils');

request = request(utils.host);


describe('Authentication', function() {
    before(function(done) {
        request.get(utils.drop_ep)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(200);
                done();
            });
    });


    describe('Registration', function() {

        describe('Guests', function() {

            it('Should not be allowed to register with non guc email', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Someone Here',
                        email: 'someone@example.com',
                        password: 'pass'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(400);
                        done();
                    });
            });
        });



        describe('Teacher', function() {
            it('should respond with json', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Amr Draz',
                        email: 'draz@guc.edu.eg',
                        password: 'pass',
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        res.body.should.have.properties({
                            email: 'draz@guc.edu.eg',
                            name: 'Amr Draz'
                        }).and.have.properties(['id', 'url']);
                        res.header.should.have.property('content-type', 'application/json');
                        res.body.should.not.have.property('pass');
                        done();
                    });

            });

            it('should respond with 400', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Bad TA',
                        email: 'baduser@guc.edu.eg'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(400);
                        res.header.should.have.property('content-type', 'application/json');
                        done();
                    });
            });

        });

        describe('Student', function() {
            it('should respond with json', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Ahmed Hisham',
                        email: 'ahmed.hisham@student.guc.edu.eg',
                        guc_id: '16-4477',
                        password: 'pass'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        res.header.should.have.property('content-type', 'application/json');
                        res.body.should.have.properties({
                            name: 'Ahmed Hisham',
                            email: 'ahmed.hisham@student.guc.edu.eg',
                            guc_id: '16-4477',
                        });
                        res.body.should.have.properties(['id', 'url']);
                        res.body.should.not.have.property('pass');
                        done();
                    });
            });

            it('should respond with 400', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Bad student',
                        email: 'student@student.guc.edu.eg',
                        password: 'pass'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(400);
                        res.header.should.have.property('content-type', 'application/json');
                        done();
                    });
            });
        });

        describe('Duplicate Emails', function() {
            before(function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Student One',
                        email: 'student1@student.guc.edu.eg',
                        password: 'pass',
                        guc_id: '22-4444'
                    }).end(function(err, res) {});
                request.post(utils.users_ep)
                    .send({
                        name: 'Teacher One',
                        email: 'teacher1@guc.edu.eg',
                        password: 'pass'
                    }).end(function(err, res) {
                        done();
                    });
            });

            it('should respond with 422 for duplicate student', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Student One',
                        email: 'student1@student.guc.edu.eg',
                        password: 'pass',
                        guc_id: '22-4444'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(422);
                        res.header.should.have.property('content-type', 'application/json');
                        done();
                    });
            });

            it('should respond with 422 for duplicate TA', function(done) {
                request.post(utils.users_ep)
                    .send({
                        name: 'Teacher One',
                        email: 'teacher1@guc.edu.eg',
                        password: 'pass'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(422);
                        res.header.should.have.property('content-type', 'application/json');
                        done();
                    });
            });

        });


    });


    describe('Login', function() {
        teacher_one = {
            name: 'Login Teacher One',
            email: 'teacher.login@guc.edu.eg',
            password: 'pass'
        };
        teacher_two = {
            name: 'Login Teacher Two',
            email: 'teacher2.login@guc.edu.eg',
            password: 'pass'
        };
        student_one = {
            name: 'Login Student One',
            email: 'student1.login@student.guc.edu.eg',
            password: 'pass',
            guc_id: '22-1111'
        };

        student_two = {
            name: 'Login Student Two',
            email: 'student2.login@student.guc.edu.eg',
            password: 'pass',
            guc_id: '22-1112'
        };

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

        describe('Teacher', function() {

            it('should be able to access other teacher profile', function(done) {
                request.get(teacher_two.url)
                    .set('X-Auth-Token', teacher_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.have.properties({
                            id: teacher_two.id,
                            email: teacher_two.email,
                            name: teacher_two.name,
                            url: teacher_two.url
                        });
                        done();
                    });
            });

            it('should be able to access student profile', function(done) {
                request.get(student_one.url)
                    .set('X-Auth-Token', teacher_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.have.properties({
                            id: student_one.id,
                            email: student_one.email,
                            name: student_one.name,
                            url: student_one.url,
                            guc_id: student_one.guc_id
                        });
                        done();
                    })
            });

            it('should be able to list all users', function(done) {
                request.get(utils.users_ep)
                    .set('X-Auth-Token', teacher_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.be.an.instanceOf(Array).and
                            .should.not.be.empty;
                        res.body.should.matchEach(function(it) {
                            it.should.have.properties(['id', 'url', 'email', 'name', 'created_at']);
                        });
                        done();
                    });
            });

            it('should be able to update profile', function(done) {
                request.put(teacher_one.url)
                    .set('X-Auth-Token', teacher_one.token)
                    .send({
                        'password': 'new password'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        teacher_one.password = 'new password';
                        res.body.should.be.an.instanceOf(Object);
                        res.body.should.have.property('id', teacher_one.id);
                        // Get new token
                        request.post(utils.token_ep)
                            .set('X-Auth', utils.auth_header_value(teacher_one.email,
                                teacher_one.password))
                            .end(function(err, res) {
                                should.not.exist(err);
                                res.status.should.be.eql(201);
                                res.body.should.have.property('token')
                                teacher_one.token = res.body.token;
                                done();
                            });
                    });
            });

            it("should not update another user's profile", function(done) {
                request.put(teacher_two.url)
                    .set('X-Auth-Token', teacher_one.token)
                    .send({
                        'name': 'James'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(403);
                        request.get(teacher_two.url)
                            .set('X-Auth-Token', teacher_one.token)
                            .end(function(err, res) {
                                should.not.exist(err);
                                res.status.should.be.eql(200);
                                res.body.should.have.property('name', teacher_two.name);
                                done();
                            });
                    });
            });
        });

        describe('Student', function() {
            it('should be able to access teacher profile', function(done) {
                request.get(teacher_two.url)
                    .set('X-Auth-Token', student_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.have.properties({
                            id: teacher_two.id,
                            email: teacher_two.email,
                            name: teacher_two.name,
                            url: teacher_two.url
                        });
                        done();
                    });
            });

            it('should be able to access other student profile', function(done) {
                request.get(student_two.url)
                    .set('X-Auth-Token', student_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.have.properties({
                            id: student_two.id,
                            email: student_two.email,
                            name: student_two.name,
                            url: student_two.url,
                            guc_id: student_two.guc_id
                        });
                        done();
                    })
            });

            it('should be able to list all users', function(done) {
                request.get(utils.users_ep)
                    .set('X-Auth-Token', student_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.be.an.instanceOf(Array).and
                            .should.not.be.empty;
                        res.body.should.matchEach(function(it) {
                            it.should.have.properties(['id', 'url', 'email', 'name', 'created_at']);
                        });
                        done();
                    });
            });

            it('should be able to update profile', function(done) {
                request.put(student_one.url)
                    .set('X-Auth-Token', student_one.token)
                    .send({
                        'password': 'new password'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        student_one.password = 'new password';
                        res.body.should.be.an.instanceOf(Object);
                        res.body.should.have.property('id', student_one.id);
                        // Get new token
                        request.post(utils.token_ep)
                            .set('X-Auth', utils.auth_header_value(student_one.email,
                                student_one.password))
                            .end(function(err, res) {
                                should.not.exist(err);
                                res.status.should.be.eql(201);
                                res.body.should.have.property('token')
                                student_one.token = res.body.token;
                                done()
                            });
                    });
            });

            it("should not update another user's profile", function(done) {
                request.put(student_two.url)
                    .set('X-Auth-Token', student_one.token)
                    .send({
                        'name': 'James'
                    }).end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(403);
                        request.get(student_two.url)
                            .set('X-Auth-Token', student_one.token)
                            .end(function(err, res) {
                                should.not.exist(err);
                                res.status.should.be.eql(200);
                                res.body.should.have.property('name', student_two.name);
                                done();
                            });
                    });
            });
        });


    });

    describe('Token', function() {

        it('Should 404 on non existing email', function(done) {
            request.post(utils.token_ep)
                .set('X-Auth', utils.auth_header_value('non.existant@guc.edu.eg',
                    'pass'))
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(401);
                    done();
                });
        });

        it('Should 401 on invalid password', function(done) {
            request.post(utils.token_ep)
                .set('X-Auth', utils.auth_header_value(student_two.email,
                    student_two.pass + '22'))
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(401);
                    done();
                });
        });

        it('Should 400 on invalid Authentication value', function(done) {
            request.post(utils.token_ep)
                .set('X-Auth', 'not a token')
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(400);
                    done();
                });
        });

        it('should 400 on no Authentication header', function(done){
            request.post(utils.token_ep)
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(400);
                done();
            });
        });

    });

});