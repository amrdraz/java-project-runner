var frisby = require('frisby');
var constants = require('./constants');


function course_tests(token){
    frisby.create('As a TA I can create a new course')
    .addHeader('X-Auth-Token', token)
    .post(constants.courses_ep, {
        name: 'csen401',
        description: 'The reason we are here.'
    }).expectStatus(201)
    .expectJSON({
        name: 'csen401',
        description: 'The reason we are here.',
        url: '/course/csen401',
        supervisor: {
            name: 'John TAer',
            email: 'example2@guc.edu.eg',
        },
        tas_url: "/course/csen401/tas",
        students_url: "/course/csen401/students",
        projects_url: "/course/csen401/projects",
        submissions_url: "/course/csen401/submissions"
    }).afterJSON(function (course_json) {
        frisby.create('As a TA I can create a new project')
        .addHeader('X-Auth-Token', token)
        .post(constants.get_course_projects_ep(course_json.name), {
            "name": "Milestone1",
            "language": "J"
        }).expectStatus(201).toss();
    }).toss();
}

function token_helper(to_call) {
    return function(x) { to_call(json.token); }
}

frisby.create('Create a new TA')
    .post(constants.users_ep, {
        email: 'example2@guc.edu.eg',
        name: 'John TAer', 
        password: 'password'
    }).expectStatus(201)
    .afterJSON(function(json) {
        frisby.create('Login')
        .addHeader('Authorization', constants.auth_header_value(json.email, 'password'))
        .post(constants.token_ep, {})
        .expectStatus(201)
        .afterJSON(token_helper(course_tests))
        .toss();
    }).toss();