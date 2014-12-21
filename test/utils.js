exports.host = 'http://localhost:8080';
exports.users_ep = '/users';
exports.token_ep = '/token';
exports.user_url = function(id){
    return ['/user', id].join('/');
}

exports.auth_header_value = function (email, password){
    return ["Basic", Buffer([email, password].join(':')).toString('base64')].join(' ');
}

exports.course_projects_ep = function (course_name) {
    return [ '/course', course_name, 'projects'].join('/');
}

exports.courses_ep = '/courses';

exports.drop_ep = '/drop';
exports.users_ep = '/users';
exports.token_ep = '/token';