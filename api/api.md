# Project Runner

# Group Submission

## Search [/submissions{?course,student,project}]

+ Parameters
    
    + course (optional, string, `csen401` ) ... name of the course.
    + student (optional, string, `16-0000`) ... student GUC id.
    + project (optional, string, `milestone 1`) ... name of project.


### GET 


+ Request
    
    +  Header
        
            X-Auth-Token: <auth-token>

+ Response 200 (application/json)

    + Body

            [
                { 
                "id": 1,
                "url": "/submission/1",
                "project":
                {
                    "name": "Milestone 1",
                    "course": {
                        "name": "csen401",
                        "url": "/course/csen401",
                        "supervisor": {
                           "name": "John TA",
                           "url": "/user/22"
                        },
                        "tas_url": "/course/csen401/tas",
                        "students_url": "/course/csen401/students"
                    },
                    "url": "/course/csen401/projects/milestone1",
                    "submission_url": "/course/csen401/projects/milestone1/submissions",
                    "projects_url": "/courses/csen401/projects"
                },  
                "submitter": {
                    "id": 2, 
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


## Upload [/submissions/{course}/{project}]

+ Parameters
    
    + course (required, string, `csen401` ) ... name of the course.
    + project (required, string, `milestone1` ) ... name of the project.

### POST 


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
                "project":
                {
                    "name": "Milestone 1",
                    "course": {
                        "name": "csen401",
                        "url": "/course/csen401",
                        "supervisor": {
                           "id": 22,
                           "name": "John TA",
                           "url": "/user/22"
                        },
                        "tas_url": "/course/csen401/tas",
                        "students_url": "/course/csen401/students",
                        "projects_url": "/courses/csen401/projects"
                    },
                    "url": "/course/csen401/projects/milestone1",
                    "submission_url": "/course/csen401/projects/milestone1/submissions"
                },
                "submitter": {
                    "id": 2, 
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
                    "id": 22,
                    "name": "John TA",
                    "url": "/user/22"
                 },
                 "tas_url": "/course/csen401/tas",
                 "students_url": "/course/csen401/students",
                 "submissions_url": "/course/csen401/submissions",
                 "projects_url": "/courses/csen401/projects"
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

+ Response 201 (application/json)
    
    + Body
    
            {
                "name": "csen401",
                "description": "Advanced computer lab, bla bla..",
                "url": "/course/csen401",
                "supervisor": {
                   "id": 22,
                   "name": "John TA",
                   "url": "/user/22"
                },
                "tas_url": "/course/csen401/tas",
                "students_url": "/course/csen401/students",
                "submissions_url": "/course/csen401/submissions",
                "projects_url": "/courses/csen401/projects"
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
                   "id": 22,
                   "name": "John TA",
                   "url": "/user/22"
                },
                "tas_url": "/course/csen401/tas",
                "students_url": "/course/csen401/students",
                "projects_url": "/courses/csen401/projects",
                "projects": [
                    {
                        "name": "Milestone 1",
                        "url": "/course/csen401/projects/milestone1",
                        "submission_url": "/course/csen401/projects/milestone1/submissions" 
                    }
                ]
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
                "project":
                {
                    "name": "Milestone 1",
                    "course": {
                        "name": "csen401",
                        "url": "/course/csen401",
                        "supervisor": {
                           "id": 22,
                           "name": "John TA",
                           "url": "/user/22"
                        },
                        "projects_url": "/courses/csen401/projects",
                        "tas_url": "/course/csen401/tas",
                        "students_url": "/course/csen401/students"
                    },
                    "url": "/course/csen401/projects/milestone1",
                    "submission_url": "/course/csen401/projects/milestone1/submissions"
                },
                "submitter": {
                    "id": 2, 
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
               "id": 22,
               "name": "John TA",
               "url": "/user/22"
            } 

### Remove TA [DELETE]

- `id` is a __required__ field, it represents the TA's id.

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 
    + Body

            "id": 2

+ Response 204

### Add TA [POST]

- `id` is a __required__ field, it represents the TA's id.

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

    + Body

            "id": 2

+ Response 204

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
                    "id": 2, 
                    "name": "John Student",
                    "guc_id": "22-0000",
                    "url": "/user/2"
                }
            ]

### Remove Student [DELETE]

- `id` is a __required__ field, it represents the student's id (not guc id).

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

    + Body

            "id": 2


+ Response 201

### Add Student [POST]

- `id` is a __required__ field, it represents the student's id (not guc id).

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 

    + Body

            "id": 2

+ Response 204



# Group Project

## Projects [/course/{name}/projects/]

+ Parameters

    + name (required, string, `csen401`) ... course name.

### List all [GET]

+ Request

    + Header

                X-Auth-Token: <auth-token>

+ Response 200 (application/json)
    
    + Body

            [
                {
                    "name": "Milestone 1",
                    "course": {
                        "name": "csen401",
                        "url": "/course/csen401",
                        "supervisor": {
                           "id": 22,
                           "name": "John TA",
                           "url": "/user/22"
                        },
                        "tas_url": "/course/csen401/tas",
                        "students_url": "/course/csen401/students",
                        "projects_url": "/courses/csen401/projects"
                    },
                    "url": "/course/csen401/projects/milestone1",
                    "submission_url": "/course/csen401/projects/milestone1/submissions"
                }
            ]

### Create New [POST]
- `name` is a __required__ field, this is the project's name.


+ Request (application/json)

    + Header

            -X-Auth-Token: <auth-token>

    + Body 

            {
                "name": "Milestone 1",
                "language": "J",
                "due_date": "2015-02-05T17:55:00.000Z",
                "test_timeout": 600,
                "file[0]": ...,
            }

+ Response 200 (application/json)
    
    + Body

            {
                "created_at": "2015-02-03T07:03:03+00:00",
                "course": {
                    "supervisor": {
                        "guc_id": null,
                        "name": "Teacher One",
                        "url": "/user/54c8b1172d1f907fef478b91",
                        "created_at": "2015-01-28T09:51:19+00:00",
                        "email": "teacher1@guc.edu.eg",
                        "active": false,
                        "id": "54c8b1172d1f907fef478b91"
                    },
                    "name": "Test Course",
                    "url": "/course/Test%20Course",
                    "tas_url": "/course/Test%20Course/tas",
                    "submissions_url": "/course/Test%20Course/submissions",
                    "projects_url": "/course/Test%20Course/projects",
                    "created_at": "2015-01-28T09:52:15+00:00",
                    "students_url": "/course/Test%20Course/students",
                    "description": "Please Ignore"
                },
                "tests": [
                    {
                        "name": "M1Tests.java",
                        "download_url": "/project/54d072a72d1f900f3e1b7d97/tests/M1Tests.java"
                    }
                ],
                "name": "New Project",
                "language": "J",
                "due_date": "2015-02-05T17:55:00+00:00",
                "url": "/project/54d072a72d1f900f3e1b7d97",
                "submissions_url": "/course/Test%20Course/projects/New%20Project/submissions",
                "id": "54d072a72d1f900f3e1b7d97",
                "can_submit": true
            }


## Submissions [/course/{name}/projects/{project_name}/submissions]
+ Parameters
    
    + name (required, string, `csen401` ) ... name of the course.

    + project_name (required, string, `milestone1`) ... name of the project.


### List all Submissions [GET]

+ Request
    
    +  Header
        
            X-Auth-Token: <auth-token>

+ Response 200 (application/json)

    + Body

            [
                { 
                "id": 1,
                "url": "/submission/1",
                "project":
                {
                    "name": "Milestone 1",
                    "course": {
                        "name": "csen401",
                        "url": "/course/csen401",
                        "supervisor": {
                           "id": 22,
                           "name": "John TA",
                           "url": "/user/22"
                        },
                        "tas_url": "/course/csen401/tas",
                        "students_url": "/course/csen401/students",
                        "projects_url": "/courses/csen401/projects"
                    },
                    "url": "/course/csen401/projects/milestone1",
                    "submission_url": "/course/csen401/projects/milestone1/submissions"
                },  
                "submitter": {
                    "id": 2, 
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

### Create New Submission [POST]

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


## Single project [/project/{project_name}]

+ Parameters
    
    + name (required, string, `csen401` ) ... name of the course.

    + project_name (required, string, `milestone1`) ... name of the project.


### GET

+ Request

    + Header

            X-Auth-Token: <auth-token>

+ Response 200 (application/json)
    
    + Body

            {
                "name": "Milestone 1",
                "course": {
                    "name": "csen401",
                    "url": "/course/csen401",
                    "supervisor": {
                       "id": 22,
                       "name": "John TA",
                       "url": "/user/22"
                    },
                    "tas_url": "/course/csen401/tas",
                    "students_url": "/course/csen401/students",
                    "projects_url": "/courses/csen401/projects"
                },
                "url": "/course/csen401/projects/milestone1",
                "submission_url": "/course/csen401/projects/milestone1/submissions"
            }

### PUT

Modifies the due_data and test files fields.
Test files are simply replaced.

+ Request (application/json)

    + Header

            -X-Auth-Token: <auth-token>

    + Body 

            {
                "due_date": "2015-02-06T17:55:00.000Z",
                "file[0]": ...,
            }

+ Response 200 (application/json)
    
    + Body

            {
                "created_at": "2015-02-03T07:03:03+00:00",
                "course": {
                    "supervisor": {
                        "guc_id": null,
                        "name": "Teacher One",
                        "url": "/user/54c8b1172d1f907fef478b91",
                        "created_at": "2015-01-28T09:51:19+00:00",
                        "email": "teacher1@guc.edu.eg",
                        "active": false,
                        "id": "54c8b1172d1f907fef478b91"
                    },
                    "name": "Test Course",
                    "url": "/course/Test%20Course",
                    "tas_url": "/course/Test%20Course/tas",
                    "submissions_url": "/course/Test%20Course/submissions",
                    "projects_url": "/course/Test%20Course/projects",
                    "created_at": "2015-01-28T09:52:15+00:00",
                    "students_url": "/course/Test%20Course/students",
                    "description": "Please Ignore"
                },
                "tests": [
                    {
                        "name": "M1Tests.java",
                        "download_url": "/project/54d072a72d1f900f3e1b7d97/tests/M1Tests.java"
                    }
                ],
                "name": "New Project",
                "language": "J",
                "due_date": "2015-02-05T17:55:00+00:00",
                "url": "/project/54d072a72d1f900f3e1b7d97",
                "submissions_url": "/course/Test%20Course/projects/New%20Project/submissions",
                "id": "54d072a72d1f900f3e1b7d97",
                "can_submit": true
            }



# Group User

## Users collection [/users]

### Create new user [POST]

- `email` is a __required__ field, this should be guc email.
- `name` is a __required__ field, this should be the user's full name.
- `password` is a __required__ field.
- `guc_id` is a __required__ field, iff email is @student.guc.edu.eg


+ Request (application/json)

    + Body
            
            {
                "password": "password",
                "email": "example@guc.edu.eg",
                "name": "John TA"
            }

+ Response 201 (application/json)

    + Body

            {
                "id": 1,
                "email": "example@guc.edu.eg",
                "name": "John TA",
                "url": "/user/1"
            }

### GET
    
+ Request (application/json)

    + Header

            X-Auth-Token: <token>

+ Response 201 (application/json)

    + Body
        
            [
                {
                    "id": 1,
                    "email": "example@guc.edu.eg",
                    "name": "John TA",
                    "url": "/user/1"
                }
            ]
            

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
                    "id": 1,

                    "email": "example@guc.edu.eg",
                    "name": "John TA",
                    "url": "/user/1"
                }
            ]

### DELETE

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token> 

+ Response 200

### PUT

- `name` is an __optional__ field, this should be the user's full name.
- `password` is an __optional__ field.
- `guc_id` is an __optional__ field, iff email is @student.guc.edu.eg

+ Request (application/json)

    + Header

            X-Auth-Token: <auth-token>

    + Body

            {"password": "harder_password"}

+ Response 200 


# Group Token

## /tokens

### Create new token [POST]

+ Request 

    + Header

            Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==

+ Response 201 (application/json)

    + Body

            {"token": "some_long_ciphertext"}
