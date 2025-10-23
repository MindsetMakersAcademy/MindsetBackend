"""OpenAPI 3.0 documentation for API endpoints and schemas."""

# Schema definitions
DELIVERY_MODE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "label": {"type": "string"},
        "description": {"type": "string", "nullable": True},
    },
    "required": ["id", "label"],
}

VENUE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "address": {"type": "string", "nullable": True},
        "map_url": {"type": "string", "nullable": True},
        "notes": {"type": "string", "nullable": True},
        "room_capacity": {"type": "integer", "nullable": True},
    },
    "required": ["id", "name"],
}

INSTRUCTOR_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
        "phone": {"type": "string", "nullable": True},
        "email": {"type": "string", "nullable": True},
        "bio": {"type": "string", "nullable": True},
    },
    "required": ["id", "full_name"],
}

COURSE_PAST_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string", "nullable": True},
        "capacity": {"type": "integer", "nullable": True},
        "session_counts": {"type": "integer", "nullable": True},
        "session_duration_minutes": {"type": "integer", "nullable": True},
        "start_date": {"type": "string", "format": "date", "nullable": True},
        "end_date": {"type": "string", "format": "date", "nullable": True},
        "delivery_mode": {"$ref": "#/components/schemas/DeliveryMode"},
        "venue": {"$ref": "#/components/schemas/Venue"},
        "instructors": {"type": "array", "items": {"$ref": "#/components/schemas/Instructor"}},
    },
    "required": ["id", "title", "delivery_mode", "instructors"],
}

COURSE_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "delivery_mode_id": {"type": "integer"},
        "venue_id": {"type": "integer"},
        "instructor_ids": {"type": "array", "items": {"type": "integer"}},
        "start_date": {"type": "string", "format": "date"},
        "end_date": {"type": "string", "format": "date"},
        "capacity": {"type": "integer"},
        "session_counts": {"type": "integer"},
        "session_duration_minutes": {"type": "integer"},
    },
    "required": ["title", "delivery_mode_id"],
}

ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"error": {"type": "string"}},
    "required": ["error"],
}

VALIDATION_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {"type": "string"},
        "details": {
            "type": "object",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
    },
    "required": ["error"],
}

# Combined schema collection
SCHEMAS = {
    "DeliveryMode": DELIVERY_MODE_SCHEMA,
    "Venue": VENUE_SCHEMA,
    "Instructor": INSTRUCTOR_SCHEMA,
    "CoursePast": COURSE_PAST_SCHEMA,
    "CourseCreate": COURSE_CREATE_SCHEMA,
    "Error": ERROR_RESPONSE_SCHEMA,
    "ValidationError": VALIDATION_ERROR_SCHEMA,
}

# Base Swagger template
SWAGGER_TEMPLATE = {
    "info": {
        "title": "ImpactCore API",
        "version": "1.0.0",
        "description": "Read-only APIs for **past courses** (Asia/Tehran).",
    },
    "servers": [{"url": "/"}],
    "components": {"schemas": SCHEMAS},
}

# API endpoint documentation
LIST_COURSES_DOC = {
    "tags": ["Courses"],
    "summary": "List all courses",
    "description": "Retrieves a list of all available courses with basic information.",
    "responses": {
        200: {
            "description": "List of courses retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "courses": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/CoursePast"},
                            }
                        },
                    }
                }
            },
        }
    },
}

GET_COURSE_DOC = {
    "tags": ["Courses"],
    "summary": "Get course details by ID",
    "description": """Retrieves detailed information about a specific course including its venue,
        instructors, and delivery mode.""",
    "parameters": [
        {
            "name": "course_id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer", "minimum": 1},
            "description": "The unique identifier of the course",
        }
    ],
    "responses": {
        200: {
            "description": "Course details retrieved successfully",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/CoursePast"}}
            },
        },
        404: {
            "description": "Course not found",
            "content": {
                "application/json": {
                    "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
                }
            },
        },
    },
}

LIST_PAST_COURSES_DOC = {
    "tags": ["Courses"],
    "summary": "List past courses",
    "description": "Retrieves a list of courses that have already ended.",
    "responses": {
        200: {
            "description": "List of past courses retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "courses": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/CoursePast"},
                            }
                        },
                    }
                }
            },
        }
    },
}

SEARCH_COURSES_DOC = {
    "tags": ["Courses"],
    "summary": "Search courses",
    "description": """Search for courses by title. Returns courses whose titles 
        contain the search query.""",
    "parameters": [
        {
            "name": "q",
            "in": "query",
            "required": False,
            "schema": {"type": "string", "minLength": 1},
            "description": "Search query to filter courses by title (case-insensitive)",
        }
    ],
    "responses": {
        200: {
            "description": "Search results retrieved successfully",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "courses": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/CoursePast"},
                            }
                        },
                    }
                }
            },
        }
    },
}

CREATE_COURSE_DOC = {
    "tags": ["Courses"],
    "summary": "Create a new course",
    "description": """
        Create a new course with the specified details.
        
        Required fields:
        - title: Course name
        - delivery_mode_id: ID of the delivery mode (e.g., online, in-person)
        
        Optional fields include venue, instructors, dates, capacity, and session details.
    """,
    "requestBody": {
        "required": True,
        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CourseCreate"}}},
    },
    "responses": {
        201: {
            "description": "Course created successfully",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/CoursePast"}}
            },
        },
        400: {
            "description": "Invalid input",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}
            },
        },
    },
}


LIST_INSTRUCTORS_DOC = {
    "tags": ["Instructors"],
    "summary": "List all instructors",
    "description": "Retrieve a list of instructors with optional filtering and sorting.",
    "parameters": [
        {
            "name": "q",
            "in": "query",
            "required": False,
            "schema": {"type": "string", "minLength": 1, "maxLength": 100},
            "description": "Search query to filter instructors by name (case-insensitive)",
            "example": "john",
        },
        {
            "name": "sort",
            "in": "query",
            "required": False,
            "schema": {"type": "string", "enum": ["id", "full_name"], "default": "full_name"},
            "description": "Field to sort by",
        },
        {
            "name": "direction",
            "in": "query",
            "required": False,
            "schema": {"type": "string", "enum": ["asc", "desc"], "default": "asc"},
            "description": "Sort direction",
        },
    ],
    "responses": {
        200: {
            "description": "List of instructors",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "instructors": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/Instructor"},
                            }
                        },
                    },
                    "example": {
                        "instructors": [
                            {
                                "id": 1,
                                "full_name": "Dr. Jane Smith",
                                "email": "jane.smith@example.com",
                                "phone": "+1234567890",
                                "bio": "Expert in Python and web development",
                            },
                            {
                                "id": 2,
                                "full_name": "Prof. John Doe",
                                "email": "john.doe@example.com",
                                "phone": "+0987654321",
                                "bio": "Database architecture specialist",
                            },
                        ]
                    },
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"},
                    "example": {"error": "Internal server error"},
                }
            },
        },
    },
}

GET_INSTRUCTOR_DOC = {
    "tags": ["Instructors"],
    "summary": "Get instructor by ID",
    "description": "Retrieve detailed information about a specific instructor.",
    "parameters": [
        {
            "name": "instructor_id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer", "minimum": 1},
            "description": "Unique identifier of the instructor",
            "example": 1,
        }
    ],
    "responses": {
        200: {
            "description": "Instructor details",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Instructor"},
                    "example": {
                        "id": 1,
                        "full_name": "Dr. Jane Smith",
                        "email": "jane.smith@example.com",
                        "phone": "+1234567890",
                        "bio": "Expert in Python and web development with 10+ years of experience",
                    },
                }
            },
        },
        404: {
            "description": "Instructor not found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"},
                    "example": {"error": "Not found"},
                }
            },
        },
    },
}

CREATE_INSTRUCTOR_DOC = {
    "tags": ["Instructors"],
    "summary": "Create a new instructor",
    "description": "Register a new instructor in the system. Email and phone must be unique.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["full_name"],
                    "properties": {
                        "full_name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 120,
                            "description": "Instructor's full name",
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "maxLength": 160,
                            "nullable": True,
                            "description": "Email address (must be unique)",
                        },
                        "phone": {
                            "type": "string",
                            "maxLength": 40,
                            "nullable": True,
                            "description": "Phone number (must be unique)",
                        },
                        "bio": {
                            "type": "string",
                            "nullable": True,
                            "description": "Instructor biography or description",
                        },
                    },
                },
                "example": {
                    "full_name": "Dr. Jane Smith",
                    "email": "jane.smith@example.com",
                    "phone": "+1234567890",
                    "bio": "Expert in Python and web development with 10+ years of experience",
                },
            }
        },
    },
    "responses": {
        201: {
            "description": "Instructor created successfully",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Instructor"},
                    "example": {
                        "id": 1,
                        "full_name": "Dr. Jane Smith",
                        "email": "jane.smith@example.com",
                        "phone": "+1234567890",
                        "bio": "Expert in Python and web development with 10+ years of experience",
                    },
                }
            },
        },
        400: {
            "description": "Invalid input or duplicate email/phone",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"},
                    "examples": {
                        "validation_error": {"value": {"error": "full_name cannot be empty"}},
                        "duplicate_email": {
                            "value": {
                                "error": "Instructor with email='jane@example.com' already exists"
                            }
                        },
                    },
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        },
    },
}

UPDATE_INSTRUCTOR_DOC = {
    "tags": ["Instructors"],
    "summary": "Update an instructor",
    "description": "Update instructor information. All fields are optional; only provided fields will be updated.",
    "parameters": [
        {
            "name": "instructor_id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer", "minimum": 1},
            "description": "Unique identifier of the instructor to update",
        }
    ],
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string", "minLength": 1, "maxLength": 120},
                        "email": {
                            "type": "string",
                            "format": "email",
                            "maxLength": 160,
                            "nullable": True,
                        },
                        "phone": {"type": "string", "maxLength": 40, "nullable": True},
                        "bio": {"type": "string", "nullable": True},
                    },
                },
                "example": {
                    "bio": "Updated bio with new achievements and certifications",
                    "phone": "+1234567899",
                },
            }
        },
    },
    "responses": {
        200: {
            "description": "Instructor updated successfully",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/Instructor"}}
            },
        },
        400: {
            "description": "Invalid input or duplicate email/phone",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        },
        404: {
            "description": "Instructor not found",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        },
    },
}

DELETE_INSTRUCTOR_DOC = {
    "tags": ["Instructors"],
    "summary": "Delete an instructor",
    "description": "Remove an instructor from the system. This operation cannot be undone.",
    "parameters": [
        {
            "name": "instructor_id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer", "minimum": 1},
            "description": "Unique identifier of the instructor to delete",
        }
    ],
    "responses": {
        204: {"description": "Instructor deleted successfully (no content)"},
        404: {
            "description": "Instructor not found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"},
                    "example": {"error": "Not found"},
                }
            },
        },
    },
}
