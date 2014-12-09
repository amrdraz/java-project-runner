# Project Runner

# Group Submission

## Submissions

### GET /submissions{?course,student}

+ Parameters
    
    + course (optional, string, `csen401` ) ... name of the course.
    + student (optional, string, `16-0000`) ... student GUC id.


+ Request
    
    +  Header
        
            X-Auth-Token: <auth-token>

+ Response 200 (application/json)

    + Body

            [
                { 
                "id": 1,
                "url": "/submission/1",
                "course": {
                    "name": "csen401",
                    "url": "/course/csen401",
                    "supervisor": {
                       "user_id": 22,
                       "name": "John TA",
                       "url": "/user/22"
                    },
                    "tas_url": "/course/csen401/tas",
                    "students_url": "/course/csen401/students",
                    "submissions_url": "/course/csen401/submissions"
                },
                "submitter": {
                    "user_id": 2, 
                    "name": "John Student",
                    "guc_id": "22-0000",
                    "url": "/user/2"
                },
                "tests": [
                    {
                        "name": "FooTest", 
                        "cases": [
                            {
                                "name": "capacityShouldScaleByTwo",
                                "pass": true, "detail": ""
                            },
                            {
                                "name": "initialCapacityShouldBeTen",
                                "pass": false, "detail": "InitialCapacity expected:<10> but was:<0>"
                            }
                        ],
                        "success": false
                    }

                ],
                "processed": true
                }
            ]

### POST /submissions/{course}

+ Parameters
    
    + course (required, string, `csen401` ) ... name of the course.

+ Request Upload gzip file (application/x-gzip)

    + Header
        
            X-Auth-Token: <auth-token>

+ Request Upload tar file (application/x-tar)

    + Header
        
            X-Auth-Token: <auth-token>

+ Request Upload zip file (application/zip)

    + Header
        
            X-Auth-Token: <auth-token>

+ Request Upload 7z file (application/x-7z-compressed)

    + Header
        
            X-Auth-Token: <auth-token>

+ Request Upload rar file (application/x-rar-compressed)

    + Header
        
            X-Auth-Token: <auth-token>

+ Request Upload bzip2 file (application/x-bzip2)

    + Header
        
            X-Auth-Token: <auth-token>


+ Response 200 (application/json)
    
    + Body
    
            {
                "id": 42,
                "url": "/submission/42"
            }


## Single Submission [/submission/{id}]

+ Parameters
    
    + id (required, int, `1`) ... id of submission

### GET

+ Request Retrieve single submission
    
    + Header

            X-Auth-Token: <auth-token>

+ Response 200 (application/json)

    + Body

            { 
                "id": 1,
                "url": "/submission/1",
                "course": {
                    "name": "csen401",
                    "url": "/course/csen401",
                    "supervisor": {
                       "user_id": 22,
                       "name": "John TA",
                       "url": "/user/22"
                    },
                    "tas_url": "/course/csen401/tas",
                    "students_url": "/course/csen401/students",
                    "submissions_url": "/course/csen401/submissions"
                },
                "submitter": {
                    "user_id": 2, 
                    "name": "John Student",
                    "guc_id": "22-0000",
                    "url": "/user/2"
                },
                "tests": [
                    {
                        "name": "FooTest", 
                        "cases": [
                            {
                                "name": "capacityShouldScaleByTwo",
                                "pass": true, "detail": ""
                            },
                            {
                                "name": "initialCapacityShouldBeTen",
                                "pass": false, "detail": "InitialCapacity expected:<10> but was:<0>"
                            }
                        ],
                        "success": false
                    }
                    
                ],
                "processed": true
            }


# Group Course

## Courses Collection [/courses]

### View Courses [GET]

+ Response 200 (application/json)

    + Body
            
            [
                {"name": "csen401",
                 "url": "/course/csen401",
                 "supervisor": {
                    "user_id": 22,
                    "name": "John TA",
                    "url": "/user/22"
                 },
                 "tas_url": "/course/csen401/tas",
                 "students_url": "/course/csen401/students",
                 "submissions_url": "/course/csen401/submissions"
                }
            ]

### Create a new Course [POST]

- `name` is a __required__ field, and represents the name of the `Course` to be created.
- `description` is an __optional__ field and represets some description of the course.
- The `X-Auth-Token` Header field will be used to get the user and that user will be set as the course supervisor.


+ Request
    
    + Header

            X-Auth-Token: <auth-token> 

    + Body
    
            {
                "name": "csen401",
                "description": "Advanced computer lab, bla bla..",
            }

+ Response 200 (application/json)
    
    + Body
    
            {
                "name": "csen401",
                "description": "Advanced computer lab, bla bla..",
                "url": "/course/csen401",
                "supervisor": {
                   "user_id": 22,
                   "name": "John TA",
                   "url": "/user/22"
                },
                "tas_url": "/course/csen401/tas",
                "students_url": "/course/csen401/students",
                "submissions_url": "/course/csen401/submissions"
            }

## Single Course [/course/{name}] 

+ Parameters
    
    + name (required, string, `csen401` ) ... name of the course.

### Retrieve Course [GET]

+ Response 200 (application/json)

    + Body

            {
                "name": "csen401",
                "description": "Advanced computer lab, bla bla..",
                "url": "/course/csen401",
                "supervisor": {
                   "user_id": 22,
                   "name": "John TA",
                   "url": "/user/22"
                },
                "tas_url": "/course/csen401/tas",
                "students_url": "/course/csen401/students",
                "submissions_url": "/course/csen401/submissions"
            }

## Course Submissions [/course/{name}/submissions]

+ Parameters
    
    + name (required, string, `csen401` ) ... name of the course.

### List Submissions [GET]

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 


+ Response 200 (application/json)

    + Body

            [
                { 
                "id": 1,
                "url": "/submission/1",
                "course": {
                    "name": "csen401",
                    "url": "/course/csen401",
                    "supervisor": {
                       "user_id": 22,
                       "name": "John TA",
                       "url": "/user/22"
                    },
                    "tas_url": "/course/csen401/tas",
                    "students_url": "/course/csen401/students",
                    "submissions_url": "/course/csen401/submissions"
                },
                "submitter": {
                    "user_id": 2, 
                    "name": "John Student",
                    "guc_id": "22-0000",
                    "url": "/user/2"
                },
                "tests": [
                    {
                        "name": "FooTest", 
                        "cases": [
                            {
                                "name": "capacityShouldScaleByTwo",
                                "pass": true, "detail": ""
                            },
                            {
                                "name": "initialCapacityShouldBeTen",
                                "pass": false, "detail": "InitialCapacity expected:<10> but was:<0>"
                            }
                        ],
                        "success": false
                    }

                ],
                "processed": true
                }
            ]

## Course TAs [/course/{name}/tas]

+ Parameters
    
    + name (required, string, `csen401` ) ... name of the course.

### List TAs [GET]

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

+ Response 200 (application/json)
    
    + Body

            {
               "user_id": 22,
               "name": "John TA",
               "url": "/user/22"
            } 

### Remove TA [DELETE]

- `user_id` is a __required__ field, it represents the TA's id.

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 
    + Body

            "user_id": 2

+ Response 201

### Add TA [POST]

- `user_id` is a __required__ field, it represents the TA's id.

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

    + Body

            "user_id": 2

+ Response 201

## Course Students [/course/{name}/students]

+ Parameters
    
    + name (required, string, `csen401` ) ... name of the course.

### List Students [GET]

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 

+ Response 200 (application/json)
    
    + Body

            [
                {
                    "user_id": 2, 
                    "name": "John Student",
                    "guc_id": "22-0000",
                    "url": "/user/2"
                }
            ]

### Remove Student [DELETE]

- `user_id` is a __required__ field, it represents the student's id (not guc id).

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

    + Body

            "user_id": 2


+ Response 201

### Add Student [POST]

- `user_id` is a __required__ field, it represents the student's id (not guc id).

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 

    + Body

            "user_id": 2

+ Response 201


# Group User

## Users collection [/users]

### Create new user [POST]

- `email` is a __required__ field, this should be guc email.
- `name` is a __required__ field, this should be the user's full name.
- `password` is a __required__ field.
- `guc_id` is a __required__ field, iff email is @student.guc.edu.eg


+ Request (application/json)

+ Response 200 (application/json)

    + Body

            {
                "user_id": 1,
                "password": "password",
                "email": "example@guc.edu.eg",
                "name": "John TA",
                "url": "/user/1"
            }


## Single User [/user/{id}]

+ Parameters

    + id (required, string, `22`) ... User's ID.

### GET

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

+ Response 200 (application/json) 
    
    + Body

            [
                {
                    "user_id": 1,
                    "password": "password",
                    "email": "example@guc.edu.eg",
                    "name": "John TA",
                    "url": "/user/1"
                }
            ]

### DELETE

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 

+ Response 201

### PUT

- `name` is an __optional__ field, this should be the user's full name.
- `password` is an __optional__ field.
- `guc_id` is an __optional__ field, iff email is @student.guc.edu.eg

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

    + Body

            {"password": "harder_password"}

+ Response 201 


# Group Token

## /tokens

### Create new token [POST]

+ Request 

    + Header

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 200 (application/json)

    + Body

            {"token": "some_long_ciphertext"}