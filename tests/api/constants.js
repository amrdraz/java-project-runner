
exports.host = 'http://localhost:8080';
exports.users_ep = [exports.host, 'users'].join('/');
exports.token_ep = [exports.host, 'token'].join('/');
exports.user_url = function(id){
    return [exports.host, 'user', id].join('/');
}

exports.auth_header_value = function (username, password){
    return ["Basic", Buffer([username, password].join(':')).toString('base64')].join(' ');
}