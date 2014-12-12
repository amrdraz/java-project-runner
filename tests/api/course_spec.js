var frisby = require('frisby');
var constants = require('./constants');


function course_tests(token){
    frisby.create('Create a new course')
    .addHeader('X-Auth-Token', token)
    .post(constants.courses_ep, {
        name: 'csen401',
        description: 'The reason we are here.'
    }).expectStatus(201)
    .expectJSON({
        name: 'csen401',
        description: 'The reason we are here.',
        url: '/courses/csen401',
        supervisor: {
            name: 'John TAer',
            email: 'example2@guc.edu.eg',
        },
        tas_url: "/course/csen401/tas",
        students_url: "course/csen401/students",
        projects_url: "course/csen401/projects",
        submission_url: "course/csen401/submissions"
    }).toss();
}

function token_helper(json, to_call) {
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
        .afterJSON(token_helper)
        .toss();
    }).toss();