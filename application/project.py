from application import app
from tempfile import mkdtemp
from shutil import rmtree
from flask import render_template
import os


@app.route('/')
def test():
    working_directory = mkdtemp()
    context = {"src_dir": "src", "tests_dir": "tests", "plain_format": True}
    template = render_template('runner/build.xml', context)
    name = os.path.join(working_directory, "hello.xml")
    with open(name, "wb") as f:
        f.write(template)
    
    rmtree(working_directory)
