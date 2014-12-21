#!/bin/env python
from application import app, db, models, api
from application.resources import user, token, course, project, submission
from application.tasks import celery
from flask import url_for
from flask.ext.script import Manager, Shell

# Provides convieniet tasks


manager = Manager(app)


def _make_context():
    """Returns app context of shell"""
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def drop():
    """Drops the database"""
    db.connection.drop_database(app.config['MONGODB_SETTINGS']['DB'])


@manager.command
def run():
    """Runs the development server."""
    app.run(use_reloader=True, threaded=True, host='0.0.0.0', port=8080)


@manager.command
def routes():
    """Displays routes."""
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote(
            "{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print line

if __name__ == "__main__":
    manager.run()
