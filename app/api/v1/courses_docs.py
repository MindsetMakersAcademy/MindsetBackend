LIST_COURSES_DOC = {
    "tags": ["Courses"],
    "summary": "List all courses",
    "responses": {
        200: {
            "description": "List of all courses",
            "content": {
                "application/json": {
                    "example": {
                        "courses": [
                            {
                                "id": 1,
                                "title": "Python Basics",
                                "description": "Intro course",
                                "start_date": "2024-01-01",
                                "end_date": "2024-01-31"
                            }
                        ]
                    }
                }
            }
        }
    }
}

GET_COURSE_DOC = {
    "tags": ["Courses"],
    "summary": "Get a specific course by ID",
    "parameters": [
        {
            "name": "course_id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer"},
            "description": "ID of the course"
        }
    ],
    "responses": {
        200: {
            "description": "Course details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Python Basics",
                        "description": "Intro course",
                        "delivery_mode": {"id": 1, "label": "Online"},
                        "venue": {"id": 1, "name": "Main Campus"},
                        "instructors": [{"id": 1, "full_name": "John Doe"}],
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-31"
                    }
                }
            }
        },
        404: {
            "description": "Course not found",
            "content": {
                "application/json": {
                    "example": {"error": "Not found"}
                }
            }
        }
    }
}

LIST_PAST_COURSES_DOC = {
    "tags": ["Courses"],
    "summary": "List all past courses",
    "responses": {
        200: {
            "description": "List of past courses",
            "content": {
                "application/json": {
                    "example": {
                        "courses": [
                            {
                                "id": 1,
                                "title": "Python Basics",
                                "end_date": "2024-01-31"
                            }
                        ]
                    }
                }
            }
        }
    }
}

SEARCH_COURSES_DOC = {
    "tags": ["Courses"],
    "summary": "Search for courses",
    "parameters": [
        {
            "name": "q",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": "Search query for course title"
        }
    ],
    "responses": {
        200: {
            "description": "List of matching courses",
            "content": {
                "application/json": {
                    "example": {
                        "courses": [
                            {
                                "id": 1,
                                "title": "Python Basics",
                                "description": "Intro course"
                            }
                        ]
                    }
                }
            }
        }
    }
}

CREATE_COURSE_DOC = {
    "tags": ["Courses"],
    "summary": "Create a new course",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
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
                        "session_duration_minutes": {"type": "integer"}
                    },
                    "required": ["title", "delivery_mode_id"]
                },
                "example": {
                    "title": "Python Basics",
                    "description": "Intro course",
                    "delivery_mode_id": 1,
                    "venue_id": 1,
                    "instructor_ids": [1],
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "capacity": 30,
                    "session_counts": 8,
                    "session_duration_minutes": 120
                }
            }
        }
    },
    "responses": {
        201: {
            "description": "Course created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Python Basics",
                        "description": "Intro course",
                        "delivery_mode": {"id": 1, "label": "Online"},
                        "venue": {"id": 1, "name": "Main Campus"},
                        "instructors": [{"id": 1, "full_name": "John Doe"}],
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-31"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input",
            "content": {
                "application/json": {
                    "example": {"error": "Title is required"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"error": "Internal server error"}
                }
            }
        }
    }
}
