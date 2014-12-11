var frisby = require('frisby');
var constants = require('./constants');


frisby.create('Ability to create a new TA')
    .post(constants.users_ep, {
        email: 'example@guc.edu.eg',
        name: 'John TA', 
        password: 'password'
    }).expectHeaderContains('Content-Type', 'json')
    .expectStatus(201)
    .expectJSON({
        email: 'example@guc.edu.eg',
        name: 'John TA',
        guc_id: ''
    }).expectJSONTypes({
        'id': String,
        'url': String,
        'created_at': String,

    }).expectJSONLength(6).toss();

frisby.create('Ability to create a new Student')
    .post(constants.users_ep, {
        email: 'example@student.guc.edu.eg',
        name: 'John Student', 
        password: 'password',
        guc_id: '22-2222'
    }).expectHeaderContains('Content-Type', 'json')
    .expectStatus(201)
    .expectJSON({
        email: 'example@student.guc.edu.eg',
        name: 'John Student',
        guc_id: '22-2222'
    }).expectJSONTypes({
        'id': String,
        'url': String,
        'created_at': String,
    }).expectJSONLength(6).toss();