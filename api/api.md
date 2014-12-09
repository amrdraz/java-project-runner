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
                    "url": "/course/csen401"
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

                ]
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
                    "url": "/course/csen401"
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
                    
                ]
            }
