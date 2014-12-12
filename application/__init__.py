from flask import Flask, jsonify
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api




app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)



errors = {
    'ValidationError': {
        'message': "Invalid field(s).",
        'status': 422
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

