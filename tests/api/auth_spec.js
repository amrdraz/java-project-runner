var frisby = require('frisby');
var constants = require('./constants');

function auth_header_value(username, password){
    return ["Basic", Buffer([username, password].join(':')).toString('base64')].join(' ');
}

function token_check(json){
    frisby.create('Can create token for created user')
    .addHeader('Authorization', auth_header_value(json.email, 'password'))
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