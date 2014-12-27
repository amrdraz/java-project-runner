exports.host = 'http://localhost:8080';

exports.auth_header_value = function(email, password) {
    return ["Basic", Buffer([email, password].join(':')).toString('base64')].join(' ');
};

exports.courses_ep = '/courses';

exports.drop_ep = '/drop';
exports.users_ep = '/users';
exports.token_ep = '/token';
exports.projects_ep = '/projects'

exports.get_project_ep = function(id) {
    return ['/project', id].join('/');
};

exports.get_project_subm_ep = function(course_name, project_name) {
    return ['/course', course_name, 'projects', project_name, 'submissions'].join('/');
};

