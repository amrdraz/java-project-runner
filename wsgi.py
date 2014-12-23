from application import app, db, models, api
from application.resources import user, token, course, project, submission


wsgi_callable = app