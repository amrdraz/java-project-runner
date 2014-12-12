
exports.host = 'http://localhost:8080';
exports.users_ep = [exports.host, 'users'].join('/');
exports.token_ep = [exports.host, 'token'].join('/');
exports.user_url = function(id){
    return [exports.host, 'user', id].join('/');
}

exports.auth_header_value = function (username, password){
    return ["Basic", Buffer([username, password].join(':')).toString('base64')].join(' ');
}

exports.get_course_projects_ep = function (course_name) {
    return [exports.host, 'course', course_name, 'projects'].join('/');
}

exports.courses_ep = [exports.host, 'courses'].join('/');