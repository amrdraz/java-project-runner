var request = require('supertest');
var should = require('should');
var utils = require('./utils');

request = request(utils.host);

describe('profile', function(){
    var teacher = {
        name: 'Teacher One',
        email: 'teacher1.profile@guc.edu.eg',
        password: 'pass'
    };

    var student = {
        name: 'Student One',
        email: 'student1.profile@student.guc.edu.eg',
        password: 'pass',
        guc_id: '22-1111'
    };

    var extra_teacher =  {
        name: 'Student Two',
        email: 'student2.profile@student.guc.edu.eg',
        password: 'pass',
        guc_id: '22-4521'
    }

    var extra_student = {
        name: 'Teacher Two',
        email: 'teacher2.profile@guc.edu.eg',
        password: 'pass'
    }

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
            .send(teacher).end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                teacher.id = res.body.id;
                teacher.url = res.body.url;
                done();
            });
    });

     before(function(done) {
        request.post(utils.users_ep)
            .send(extra_teacher).end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                extra_teacher.id = res.body.id;
                extra_teacher.url = res.body.url;
                done();
            });
    });

     before(function(done) {
        request.post(utils.users_ep)
            .send(extra_student).end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                extra_student.id = res.body.id;
                extra_student.url = res.body.url;
                done();
            });
    });

    before(function(done) {
        request.post(utils.users_ep)
            .send(student).end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                student.id = res.body.id;
                student.url = res.body.url;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(teacher.email,
                    teacher.password))
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                teacher.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(extra_student.email,
                    extra_student.password))
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                extra_student.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(extra_teacher.email,
                    extra_teacher.password))
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                extra_teacher.token = res.body.token;
                done();
            });
    });

    before(function(done) {
        request.post(utils.token_ep)
            .set('X-Auth',
                utils.auth_header_value(student.email,
                    student.password))
            .end(function(err, res) {
                should.not.exist(err);
                res.status.should.be.eql(201);
                student.token = res.body.token;
                done();
            });
    });

    it('As a student I can update my profile', function(done) {
        profile = {
            guc_id: '22-1112',
            name: 'The Student'
        };
        request.put(student.url)
        .set('X-Auth-Token', student.token)
        .send(profile)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(200);
            res.body.should.have.properties({
                id: student.id,
                url: student.url,
                email: student.email,
                name: profile.name,
                guc_id: profile.guc_id
            });
            token = student.token;
            student = res.body;
            student.token = token;
            done();
        });
    });

    it('As a teacher I can update my profile', function(done) {
        profile = {
            name: 'The Teacherr'
        };
        request.put(teacher.url)
        .set('X-Auth-Token', teacher.token)
        .send(profile)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(200);
            res.body.should.have.properties({
                id: teacher.id,
                url: teacher.url,
                email: teacher.email,
                name: profile.name,
            });
            token = teacher.token;
            teacher = res.body;
            teacher.token = token;
            done();
        });
    });

    it('As a teacher I can not set a guc_id with PUT', function(done){
        profile = {
            guc_id: '22-1112',
        };
        request.put(teacher.url)
        .set('X-Auth-Token', teacher.token)
        .send(profile)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(400);
            done();
        });
    });

    it("As a teacher I can not update another teacher's profile", function(done){
        profile = {
            name: 'The Teacherr'
        };
        request.put(extra_teacher.url)
        .send(profile)
        .set('X-Auth-Token', teacher.token)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(403);
            done();
        });
    });

    it("As a teacher I can not update another student's profile", function(done){
        profile = {
            name: 'The Teacherr'
        };
        request.put(extra_student.url)
        .send(profile)
        .set('X-Auth-Token', teacher.token)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(403);
            done();
        });
    });

    it("As a student I can not update another teacher's profile", function(done){
        profile = {
            name: 'The Teacherr'
        };
        request.put(extra_teacher.url)
        .send(profile)
        .set('X-Auth-Token', student.token)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(403);
            done();
        });
    });

    it("As a student I can not update another student's profile", function(done){
        profile = {
            name: 'The Teacherr'
        };
        request.put(extra_student.url)
        .send(profile)
        .set('X-Auth-Token', student.token)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(403);
            done();
        });
    });

    it('As a student I can not update my email', function(done) {
        profile = {
            email: 'something@student.guc.edu.eg'
        }
        request.put(student.url)
        .send(profile)
        .set('X-Auth-Token', student.token)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(200);
            res.body.email.should.be.eql(student.email);
            done();
        });
    });

    it('As a teacher I can not update my email', function(done) {
        profile = {
            email: 'something@guc.edu.eg'
        }
        request.put(teacher.url)
        .send(profile)
        .set('X-Auth-Token', teacher.token)
        .end(function(err, res){
            should.not.exist(err);
            res.status.should.be.eql(200);
            res.body.email.should.be.eql(teacher.email);
            done();
        });
    });


});