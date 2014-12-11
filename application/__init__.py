from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api



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
    }
}

app = Flask(__name__)
app.config.from_object('config')
api = Api(app, catch_all_404s=True, errors=errors) 
db = MongoEngine(app)


