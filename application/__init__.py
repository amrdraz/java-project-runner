from flask import Flask, jsonify
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api




app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)



errors = {
    'ValidationError': {
        'message': "Invalid field(s).",
        'status': 400
    },
    'NotUniqueError': {
        'message': "Resource already exists with unique field.",
        'status': 422
    },
    'DoesNotExist': {
        'message': 'Resource Not found.',
        'status': 404
    },
    'ValueError': {
        'message': 'Invalid field(s)',
        'status': 400
    }
}


api = Api(app, catch_all_404s=True, errors=errors)

def add_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'HEAD, GET, POST, PATCH, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, X-Auth-Token, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response

app.after_request(add_cors_header)
