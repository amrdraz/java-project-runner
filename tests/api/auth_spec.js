var frisby = require('frisby');
var constants = require('./constants');



function token_check(json){
    frisby.create('Can create token for created user')
    .addHeader('Authorization', constants.auth_header_value(json.email, 'password'))
    .post(constants.token_ep, {})
    .expectHeaderContains('Content-Type', 'json')
    .expectStatus(201)
    .expectJSONTypes({
        token: String
    }).expectJSONLength(1)
    .afterJSON(function (tokenJSON){
        frisby.create('Login with user and retrieve info')
        .addHeader('X-Auth-Token', tokenJSON.token)
        .get(constants.user_url(json.id))
        .expectStatus(200)
        .expectHeaderContains('Content-Type', 'json')
        .expectJSON(json)
        .toss();
    }).toss();
}

frisby.create('Ability to create a new TA')
    .post(constants.users_ep, {
        email: 'example@guc.edu.eg',
        name: 'John TA', 
        password: 'password'
    }).expectHeaderContains('Content-Type', 'json')
    .expectStatus(201)
    .afterJSON(token_check)
    .expectJSON({
        email: 'example@guc.edu.eg',
        name: 'John TA',
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
    .afterJSON(token_check)
    .expectJSON({
        email: 'example@student.guc.edu.eg',
        name: 'John Student',
        guc_id: '22-2222'
    }).expectJSONTypes({
        'id': String,
        'url': String,
        'created_at': String,
    }).expectJSONLength(6).toss();


frisby.create('Missing fields bad request')
    .post(constants.users_ep, {
        email: "ta1@guc.edu.eg"
    }).expectStatus(400).toss();


frisby.create('Another Student')
    .post(constants.users_ep, {
        email: 'someone@guc.edu.eg',
        name: 'John Student', 
        password: 'password',
        // guc_id: '22-2222'
    }).expectStatus(201).after(function(err, res, body) {
       frisby.create('Duplicate student')
        .post(constants.users_ep, {
            email: 'someone@guc.edu.eg',
            name: 'John Student', 
            password: 'password',
            // guc_id: '22-2222'
        }).expectStatus(422).toss(); 
    }).toss();