#!/bin/env python
from flask import url_for
from flask.ext.script import Manager, Shell
import signal
import sys
from coverage import coverage
# Provides convieniet tasks
# Please run from repository root

def make_manager():
    from application import app
    return Manager(app)

manager = make_manager()


def _make_context():
    """Returns app context of shell"""
    from application import app, db, models, api
    from application.resources import user, token, course, project, submission
    from application.tasks import celery
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def drop():
    """Drops the database"""
    from application import app, db, models, api
    from application.resources import user, token, course, project, submission
    from application.tasks import celery
    db.connection.drop_database(app.config['MONGODB_SETTINGS']['DB'])


@manager.command
def run():
    """Runs the development server."""
    from application import app, db, models, api
    from application.resources import user, token, course, project, submission
    from application.tasks import celery
    app.run(use_reloader=True, threaded=True, host='0.0.0.0', port=8080)

@manager.command
def report_coverage():
    """
    Generate coverage report under coverage directory.
    Send SIGINT when done.
    """
    cov = coverage(branch=True, omit=['env/*'])
    cov.start()
    from application import app, db, models, api
    from application.resources import user, token, course, project, submission
    from application.tasks import celery
    def signal_handler(signal, frame):
        cov.stop()
        cov.save()
        cov.html_report(directory='coverage')
        cov.erase()
        sys.exit(0)    
    signal.signal(signal.SIGINT, signal_handler)
    app.run(use_reloader=True, threaded=True, host='0.0.0.0', port=8080)


@manager.command
def profile():
    """Runs in profiling mode."""
    from application import app, db, models, api
    from application.resources import user, token, course, project, submission
    from application.tasks import celery
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(use_reloader=True, threaded=True, host='0.0.0.0', port=8080)

@manager.command
def routes():
    """Displays routes."""
    from application import app, db, models, api
    from application.resources import user, token, course, project, submission
    from application.tasks import celery
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
