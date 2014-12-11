
exports.host = 'http://localhost:8080';
exports.users_ep = [exports.host, 'users'].join('/');
exports.token_ep = [exports.host, 'token'].join('/');
exports.user_url = function(id){
    return [exports.host, 'user', id].join('/');
}