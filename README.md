java-project-runner
===================

A web service that runs projects against tests, performs code analysis and cheating detection.

## How to run


`pip install -r 'requirements.txt'`


*Start Server* `python manage.py run`


*Clear Database* `python manage.py drop`


*Shell* `python manage.py shell`

## Tests

### Dependecies
`npm install frisby`

`npm install jasmine-node`


### Run Tests

`jasmine-node tests/api`

