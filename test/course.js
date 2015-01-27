var request = require('supertest');
var should = require('should');
var utils = require('./utils');


request = request(utils.host);

describe('Courses', function() {

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


    describe('Creation', function() {
        course_one = {
            name: 'CSEN 4XX',
            description: 'This is a very exciting course, people love it!'
        };

        it('As a teacher I can create a course', function(done) {
            request.post(utils.courses_ep)
                .set('X-Auth-Token', teacher_one.token)
                .send(course_one)
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(201);
                    res.body.should.be.an.instanceOf(Object);
                    res.body.should.have.properties({
                        name: course_one.name,
                        description: course_one.description
                    }).and.have.properties(
                        ['url', 'tas_url', 'students_url',
                            'submissions_url', 'supervisor'
                        ]);
                    course_one = res.body;
                    done();
                });
        });

        it('As a student I can not create a course', function(done) {
            request.post(utils.courses_ep)
                .set('X-Auth-Token', student_one.token)
                .send(course_three)
                .end(function(err, res) {
                    should.not.exist(err);
                    res.status.should.be.eql(403);
                    done();
                });
        });

        describe('Initial Status', function() {
            course_two = {
                name: 'CSEN 6XX',
                description: 'An Even better course if you can believe it!'
            };
            before(function(done) {
                request.post(utils.courses_ep)
                    .set('X-Auth-Token', teacher_one.token)
                    .send(course_two)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        course_two = res.body;
                        done();
                    });
            });



            it('Should have restricted public view', function(done) {
                request.get(course_two.url)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.have.properties({
                            name: course_two.name,
                            description: course_two.description,
                            url: course_two.url
                        }).and.not.have.properties(
                            ['tas_url', 'students_url', 'projects_url',
                                'submissions_url', 'supervisor'
                            ]);
                        done();
                    });

            });

            it('Should have creator as supervisor', function(done) {
                request.get(course_two.url)
                    .set('X-Auth-Token', teacher_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.containDeep({
                            supervisor: {
                                email: teacher_one.email,
                                name: teacher_one.name,
                                id: teacher_one.id,
                                url: teacher_one.url
                            }
                        });
                        done();
                    });
            });

            it('Should have exactly one TA', function(done) {
                request.get(course_two.tas_url)
                    .set('X-Auth-Token', student_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.have.a.lengthOf(1)
                            .and.matchEach(
                                function(it) {
                                    it.should.eql(course_two.supervisor);
                                });
                        done();
                    });
            });

            it('Should have zero students', function(done) {
                request.get(course_two.students_url)
                    .set('X-Auth-Token', student_one.token)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(200);
                        res.body.should.be.empty;
                        done();
                    });
            });

            describe('Course level functionality', function() {
                it('As a teacher I can add myself to course teachers and list course teachers', function(done) {
                    request.post(course_two.tas_url)
                        .send({
                            id: teacher_two.id
                        })
                        .set('X-Auth-Token', teacher_two.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(204);
                            request.get(course_two.tas_url)
                                .set('X-Auth-Token', teacher_two.token)
                                .end(function(err, res) {
                                    should.not.exist(err);
                                    res.status.should.be.eql(200);
                                    res.body.should.be.an.instanceOf(Array)
                                        .and.have.a.lengthOf(2);
                                    done();
                                });
                        });
                });

                it('As a student I can list course teachers', function(done) {
                    request.get(course_two.tas_url)
                        .set('X-Auth-Token', student_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(200);
                            res.body.should.be.an.instanceOf(Array);
                            done();
                        });
                });

                it('As a student I can not add myself as a course teacher', function(done) {
                    request.post(course_two.tas_url)
                        .send({
                            id: student_one.id
                        })
                        .set('X-Auth-Token', student_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();
                        });
                });

                it('As a teacher I can not add a student as a course teacher', function(done) {
                    request.post(course_two.tas_url)
                        .send({
                            id: student_one.id
                        })
                        .set('X-Auth-Token', teacher_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(400);
                            done();
                        });
                });

                it('As a student I should be able to add myself as a course student', function(done) {
                    request.post(course_two.students_url)
                        .send({
                            id: student_one.id
                        })
                        .set('X-Auth-Token', student_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(204);
                            done();
                        });
                });

                it('As a student I can not add another student to a course', function(done) {
                    request.post(course_two.students_url)
                        .send({
                            id: student_two.id
                        })
                        .set('X-Auth-Token', student_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();
                        });
                });

                it("As a student I can not add a teacher to a course's students", function(done) {
                    request.post(course_two.students_url)
                        .send({
                            id: teacher_two.id
                        })
                        .set('X-Auth-Token', student_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(400);
                            done();
                        });
                });

                it('As a teacher I can not add myself as a course student', function(done) {
                    request.post(course_two.students_url)
                        .send({
                            id: teacher_two.id
                        })
                        .set('X-Auth-Token', teacher_two.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(400);
                            done();
                        });
                });

                it('As a teacher I can not add another teacher as a course student', function(done) {
                    request.post(course_two.students_url)
                        .send({
                            id: teacher_one.id
                        })
                        .set('X-Auth-Token', teacher_two.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(400);
                            done();
                        });
                });

                it('As a teacher I can add a student to a course I teach', function(done) {
                    request.post(course_two.students_url)
                        .send({
                            id: student_two.id
                        })
                        .set('X-Auth-Token', teacher_two.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(204);
                            done();
                        });
                });

                describe('Course Extras', function(){
                    extra_course = {
                        name: 'DMET 6XX',
                        description: 'An Even better course if you can believe it!'
                    };

                    extra_teacher = {
                        name: 'Extra Teacher One',
                        email: 'teacher1.extra@guc.edu.eg',
                        password: 'pass'
                    };

                    before(function(done) {
                        request.post(utils.users_ep)
                        .send(extra_teacher).end(function(err, res) {
                            res.status.should.be.eql(201);
                            extra_teacher.id = res.body.id;
                            extra_teacher.url = res.body.url;
                            done();
                        });
                    });

                    before(function(done) {
                        request.post(utils.token_ep)
                        .set('X-Auth',
                            utils.auth_header_value(extra_teacher.email,
                                extra_teacher.password))
                        .end(function(err, res) {
                            res.status.should.be.eql(201);
                            extra_teacher.token = res.body.token;
                            done();
                        });
                    });

                    before(function(done) {
                        request.post(utils.courses_ep)
                        .set('X-Auth-Token', teacher_one.token)
                        .send(extra_course)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(201);
                            extra_course = res.body;
                            done();
                        });
                    });

                    it('I can not create two courses with the same name', function(done){
                        request.post(utils.courses_ep)
                        .set('X-Auth-Token', extra_teacher.token)
                        .send(extra_course)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(422);
                            done();
                        });
                    });                

                    it('As a teacher I can not add a student to a course I do not teach', function(done){
                        request.post(extra_course.students_url)
                        .set('X-Auth-Token', extra_teacher.token)
                        .send({id: student_one.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();
                        });
                    });

                    it('As a teacher I can not add another teacher to a course I do not each', function(done){
                        request.post(extra_course.tas_url)
                        .set('X-Auth-Token', extra_teacher.token)
                        .send({id: teacher_two.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();

                        });
                    });

                    it('As a student I can not add a teacher as a course teacher', function(done) {
                        request.post(extra_course.tas_url)
                        .set('X-Auth-Token', student_one.token)
                        .send({id: teacher_two.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();

                        });
                    });

                    it('As a student I can not add another student as a course teacher', function(done) {
                        request.post(extra_course.tas_url)
                        .set('X-Auth-Token', student_one.token)
                        .send({id: student_two.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();
                        });
                    });

                    it('As a student I can only add myself once to a course', function(done){
                        request.post(extra_course.students_url)
                        .set('X-Auth-Token', student_one.token)
                        .send({id: student_one.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(204);
                            request.post(extra_course.students_url)
                            .set('X-Auth-Token', student_one.token)
                            .send({id: student_one.id})
                            .end(function(err, res){
                                should.not.exist(err);
                                res.status.should.be.eql(422);
                                done();
                            });
                        });
                    });

                    it('As a teacher I can not add a student twice to a course', function(done){
                        request.post(extra_course.students_url)
                        .set('X-Auth-Token', teacher_one.token)
                        .send({id: student_two.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(204);
                            request.post(extra_course.students_url)
                            .set('X-Auth-Token', teacher_one.token)
                            .send({id: student_two.id})
                            .end(function(err, res){
                                should.not.exist(err);
                                res.status.should.be.eql(422);
                                done();
                            });
                        });
                    });

                    it('As a teacher I can not add a teacher twice to a course', function(done){
                        request.post(extra_course.tas_url)
                        .set('X-Auth-Token', teacher_one.token)
                        .send({id: teacher_two.id})
                        .end(function(err, res){
                            should.not.exist(err);
                            res.status.should.be.eql(204);
                            request.post(extra_course.tas_url)
                            .set('X-Auth-Token', teacher_one.token)
                            .send({id: teacher_two.id})
                            .end(function(err, res){
                                should.not.exist(err);
                                res.status.should.be.eql(422);
                                done();
                            });
                        });
                    });

                });


            });

        }); // Initial describe

        describe('Projects', function() {

            course_three = {
                name: 'CSEN 9XX',
                description: 'A terrible course, just terrible!'
            };

            course_four = {
                name: 'CSEN 10XX',
                description: 'A tenth semester course.'
            };

            project_one = {
                name: 'Project 1',
                language: 'J'
            };

            project_two = {
                name: 'Project 2',
                language: 'J'
            };

            before(function(done) {
                request.post(utils.courses_ep)
                    .set('X-Auth-Token', teacher_one.token)
                    .send(course_three)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        course_three = res.body;
                        request.post(course_three.tas_url)
                            .set('X-Auth-Token', teacher_one.token)
                            .send({
                                id: teacher_two.id
                            })
                            .end(function(err, res) {
                                should.not.exist(err);
                                res.status.should.be.eql(204);
                                done();
                            });

                    });
            });

            before(function(done) {
                request.post(utils.courses_ep)
                    .set('X-Auth-Token', teacher_one.token)
                    .send(course_four)
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        course_four = res.body;
                        request.post(course_four.tas_url)
                            .set('X-Auth-Token', teacher_one.token)
                            .send({
                                id: teacher_two.id
                            })
                            .end(function(err, res) {
                                should.not.exist(err);
                                res.status.should.be.eql(204);
                                done();
                            });

                    });
            });

            before(function(done) {
                request.post(course_three.projects_url)
                    .set('X-Auth-Token', teacher_one.token)
                    .field('name', project_one.name)
                    .field('language', project_one.language)
                    .field('due_date', '2020-01-26T16:14:49Z' )
                    .attach('FooTest', 'test/fixtures/project_alpha/FooTest.java')
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        project_one = res.body;
                        done();
                    });
            });

            before(function(done) {
                request.post(course_four.projects_url)
                    .set('X-Auth-Token', teacher_one.token)
                    .field('name', project_two.name)
                    .field('language', project_two.language)
                    .field('due_date', '2020-01-26T16:14:49Z' )
                    .attach('FooTest.java', 'test/fixtures/project_alpha/FooTest.java')
                    .end(function(err, res) {
                        should.not.exist(err);
                        res.status.should.be.eql(201);
                        project_two = res.body;
                        done();
                    });
            });

            describe('creation', function() {
                it('As a teacher I can create a project', function(done) {
                    project_two = {
                        name: 'SUper Awesome Project',
                        language: 'J'
                    };
                    request.post(course_three.projects_url)
                        .field('name', project_two.name)
                        .field('language', project_two.language)
                        .field('due_date', '2020-01-26T16:14:49Z' )
                        .attach('FooTest.java', 'test/fixtures/project_alpha/FooTest.java')
                        .set('X-Auth-Token', teacher_two.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(201);
                            res.body.should.have.properties({
                                name: project_two.name,
                                course: course_three
                            })
                            project_two = res.body;
                            done();
                        });
                });


                it('As a student I can not create a project', function(done) {
                    request.post(course_four.projects_url)
                        .attach('FooTest.java', 'test/fixtures/project_alpha/FooTest.java')
                        .field('name', 'This should 403')
                        .field('language', 'J')
                        .field('due_date', '2020-01-26T16:14:49Z' )
                        .set('X-Auth-Token', student_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(403);
                            done();
                        });
                });

                it('I can not create two projects with same name for the same course', function(done) {
                    request.post(course_four.projects_url)
                        .attach('FooTest.java', 'test/fixtures/project_alpha/FooTest.java')
                        .field('name', 'DUPLICATE PROJECT')
                        .field('language', 'J')
                        .set('X-Auth-Token', teacher_one.token)
                        .field('due_date', '2020-01-26T16:14:49Z' )
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(201);
                            request.post(course_four.projects_url)
                                .field('name', 'DUPLICATE PROJECT')
                                .field('language', 'J')
                                .field('due_date', '2020-01-26T16:14:49Z' )
                                .set('X-Auth-Token', teacher_one.token)
                                .end(function(err, res) {
                                    should.not.exist(err);
                                    res.status.should.be.eql(422);
                                    done();
                                });
                        });
                });

                it('I can create two projects with the same name for different courses', function(done) {
                    request.post(course_four.projects_url)
                        .attach('FooTest.java', 'test/fixtures/project_alpha/FooTest.java')
                        .field('name', 'GOOD DUPLICATE')
                        .field('language', 'J')
                        .field('due_date', '2020-01-26T16:14:49Z' )
                        .set('X-Auth-Token', teacher_one.token)
                        .end(function(err, res) {
                            should.not.exist(err);
                            res.status.should.be.eql(201);
                            request.post(course_three.projects_url)
                                .attach('FooTest.java', 'test/fixtures/project_alpha/FooTest.java')
                                .field('name', 'GOOD DUPLICATE')
                                .field('due_date', '2020-01-26T16:14:49Z' )
                                .field('language', 'J')
                                .set('X-Auth-Token', teacher_one.token)
                                .end(function(err, res) {
                                    should.not.exist(err);
                                    res.status.should.be.eql(201);
                                    done();
                                });
                        });
                });
            }); // project Creation describe
        }); // projects describe
    }); // course creation describe
}); // Courses describe