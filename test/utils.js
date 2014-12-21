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

exports.course_ep = function(course_name) {
    return ['/courses', course_name].join('/');
}

exports.course_tas_ep = function(course_name) {
    return exports.course_ep(course_name) + '/tas';
}

exports.course_projects_ep = function(course_name) {
    return exports.course_ep(course_name) + '/projects';
}

exports.course_students_ep = function(course_name) {
    return exports.course_ep(course_name) + '/students';
}

exports.course_submissions_ep = function(course_name) {
    return exports.course_ep(course_name) + '/submissions';
}

exports.courses_ep = '/courses';

exports.drop_ep = '/drop';
exports.users_ep = '/users';
exports.token_ep = '/token';