from http import HTTPStatus

user_creation = {
    HTTPStatus.CREATED: {
        "description": "User successfully created.",
        "content": {
            "application/json": {
                "examples": {
                    "Standard User": {
                        "value": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "login": "user123",
                            "first_name": "Albert",
                            "last_name": "Einstein"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.CONFLICT: {
        "description": "User already exists.",
        "content": {
            "application/json": {
                "examples": {
                    "Existing User": {
                        "value": {
                            "detail": "User already exists."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.BAD_REQUEST: {
        "description": "Invalid data provided.",
        "content": {
            "application/json": {
                "examples": {
                    "Invalid Data": {
                        "value": {
                            "detail": "Provided data is not valid."
                        }
                    }
                }
            }
        }
    }
}

login = {
    HTTPStatus.OK: {
        "description": "User authenticated.",
        "content": {
            "application/json": {
                "examples": {
                    "Successful Login": {
                        "value": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh_token": "eyJhbGcixiOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Wrong login or password.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Access": {
                        "value": {
                            "detail": "Wrong login or password."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error": {
                        "value": {
                            "detail": "An internal server error occurred."
                        }
                    }
                }
            }
        }
    }
}

logout = {
    HTTPStatus.OK: {
        "description": "Successfully logged out.",
        "content": {
            "application/json": {
                "examples": {
                    "Successful Logout": {
                        "value": {
                            "message": "Successfully logged out"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Logout": {
                        "value": {
                            "detail": "Invalid or missing token."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error": {
                        "value": {
                            "detail": "An internal server error occurred."
                        }
                    }
                }
            }
        }
    }
}

logout_all = {
    HTTPStatus.OK: {
        "description": "Successfully logged out from all sessions.",
        "content": {
            "application/json": {
                "examples": {
                    "Successful Logout from All Sessions": {
                        "value": {
                            "message": "Successfully logged out from all sessions"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Logout from All Sessions": {
                        "value": {
                            "detail": "Invalid or missing token."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Logout from All Sessions": {
                        "value": {
                            "detail": "An internal server error occurred."
                        }
                    }
                }
            }
        }
    }
}

refresh = {
    HTTPStatus.OK: {
        "description": "Tokens successfully refreshed.",
        "content": {
            "application/json": {
                "examples": {
                    "Successful Token Refresh": {
                        "value": {
                            "access_token": "newAccessJWTTokenExample...",
                            "refresh_token": "newRefreshJWTTokenExample...",
                            "token_type": "bearer"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Invalid or expired refresh token.",
        "content": {
            "application/json": {
                "examples": {
                    "Invalid Refresh Token": {
                        "value": {
                            "detail": "Invalid or expired refresh token provided."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Token Refresh": {
                        "value": {
                            "detail": "An internal server error occurred during token refresh."
                        }
                    }
                }
            }
        }
    }
}

login_history = {
    HTTPStatus.OK: {
        "description": "Login history successfully retrieved.",
        "content": {
            "application/json": {
                "examples": {
                    "Login History Example": {
                        "value": [
                            {
                                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                              "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                                "ip_address": "192.168.1.1",
                                "login_date": "2023-01-01T12:00:00"
                            },
                            {
                                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) "
                                              "AppleWebKit/602.1.50 (KHTML, like Gecko) "
                                              "CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
                                "ip_address": "192.168.1.2",
                                "login_date": "2023-01-02T15:30:00"
                            }
                        ]
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Access": {
                        "value": {
                            "detail": "Invalid or missing token."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Retrieving Login History": {
                        "value": {
                            "detail": "An internal server error occurred while retrieving login history."
                        }
                    }
                }
            }
        }
    }
}

update = {
    HTTPStatus.OK: {
        "description": "User information successfully updated.",
        "content": {
            "application/json": {
                "examples": {
                    "Successful Update": {
                        "value": {
                            "message": "User information successfully updated"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Update Attempt": {
                        "value": {
                            "detail": "Invalid or missing token."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.BAD_REQUEST: {
        "description": "Invalid data provided.",
        "content": {
            "application/json": {
                "examples": {
                    "Invalid Data": {
                        "value": {
                            "detail": "Provided data is not valid or incomplete."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.NOT_FOUND: {
        "description": "User not found.",
        "content": {
            "application/json": {
                "examples": {
                    "User Not Found": {
                        "value": {
                            "detail": "User with the provided credentials does not exist."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on User Update": {
                        "value": {
                            "detail": "An internal server error occurred while updating user information."
                        }
                    }
                }
            }
        }
    }
}

access_role = {
    HTTPStatus.OK: {
        "description": "List of roles successfully retrieved.",
        "content": {
            "application/json": {
                "examples": {
                    "Roles Example": {
                        "value": [
                            {"name": "Admin"},
                            {"name": "User"},
                            {"name": "Moderator"}
                        ]
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Access": {
                        "value": {
                            "detail": "Invalid or missing token."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Retrieving Roles": {
                        "value": {
                            "detail": "An internal server error occurred while retrieving user roles."
                        }
                    }
                }
            }
        }
    }
}

create_role = {
    HTTPStatus.CREATED: {
        "description": "Role successfully created.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Creation Example": {
                        "value": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "NewRole",
                            "description": "Description of the new role"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.FORBIDDEN: {
        "description": "Forbidden action.",
        "content": {
            "application/json": {
                "examples": {
                    "Not Authorized to Create Role": {
                        "value": {
                            "detail": "You do not have permission to perform this action"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.CONFLICT: {
        "description": "Role already exists.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Already Exists": {
                        "value": {
                            "detail": "Role already exists"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Role Creation": {
                        "value": {
                            "detail": "An internal server error occurred while creating the role"
                        }
                    }
                }
            }
        }
    }
}

delete_role = {
    HTTPStatus.NO_CONTENT: {
        "description": "Role successfully deleted.",
        "content": {}
    },
    HTTPStatus.FORBIDDEN: {
        "description": "Forbidden action.",
        "content": {
            "application/json": {
                "examples": {
                    "Not Authorized to Delete Role": {
                        "value": {
                            "detail": "You do not have permission to perform "
                                      "this action or attempting to delete a protected role"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.NOT_FOUND: {
        "description": "Role not found.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Not Found": {
                        "value": {
                            "detail": "Role with the specified UUID does not exist"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Role Deletion": {
                        "value": {
                            "detail": "An internal server error occurred while deleting the role"
                        }
                    }
                }
            }
        }
    }
}

list_roles = {
    HTTPStatus.OK: {
        "description": "List of roles successfully retrieved.",
        "content": {
            "application/json": {
                "examples": {
                    "Roles List Example": {
                        "value": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "name": "Admin",
                                "description": "Administrator role"
                            },
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174001",
                                "name": "User",
                                "description": "Standard user role"
                            },
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174002",
                                "name": "Moderator",
                                "description": "Moderator role"
                            }
                        ]
                    }
                }
            }
        }
    },
    HTTPStatus.FORBIDDEN: {
        "description": "Forbidden action.",
        "content": {
            "application/json": {
                "examples": {
                    "Not Authorized to View Roles": {
                        "value": {
                            "detail": "You do not have permission to view roles."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Retrieving Roles": {
                        "value": {
                            "detail": "An internal server error occurred while retrieving the roles list."
                        }
                    }
                }
            }
        }
    }
}

get_role = {
    HTTPStatus.OK: {
        "description": "Role successfully retrieved.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Example": {
                        "value": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Admin",
                            "description": "Administrator role"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.NOT_FOUND: {
        "description": "Role not found.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Not Found": {
                        "value": {
                            "detail": "Role with the specified UUID does not exist."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Retrieving Role": {
                        "value": {
                            "detail": "An internal server error occurred while retrieving the role."
                        }
                    }
                }
            }
        }
    }
}

get_role_name = {
    HTTPStatus.OK: {
        "description": "Role successfully retrieved.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Example": {
                        "value": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Admin",
                            "description": "Administrator role"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.NOT_FOUND: {
        "description": "Role not found.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Not Found": {
                        "value": {
                            "detail": "Role with the specified name does not exist."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Retrieving Role": {
                        "value": {
                            "detail": "An internal server error occurred while retrieving the role."
                        }
                    }
                }
            }
        }
    }
}

get_user_roles = responses = {
    HTTPStatus.OK: {
        "description": "List of roles for the user successfully retrieved.",
        "content": {
            "application/json": {
                "examples": {
                    "Roles List for User Example": {
                        "value": [
                            {"name": "admin"},
                            {"name": "subscribed"},
                            {"name": "moderator"}
                        ]
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access.",
        "content": {
            "application/json": {
                "examples": {
                    "Unauthorized Access": {
                        "value": {
                            "detail": "Invalid or missing token."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.FORBIDDEN: {
        "description": "Forbidden action.",
        "content": {
            "application/json": {
                "examples": {
                    "Not Authorized to View User Roles": {
                        "value": {
                            "detail": "You do not have permission to view roles for this user."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.NOT_FOUND: {
        "description": "User not found.",
        "content": {
            "application/json": {
                "examples": {
                    "User Not Found": {
                        "value": {
                            "detail": "User with the specified UUID does not exist."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Retrieving User Roles": {
                        "value": {
                            "detail": "An internal server error occurred while retrieving roles for the user."
                        }
                    }
                }
            }
        }
    }
}

assign_role = {
    HTTPStatus.OK: {
        "description": "Role successfully assigned to the user.",
        "content": {
            "application/json": {
                "examples": {
                    "Assigned Roles List": {
                        "value": [
                            {"name": "Admin"},
                            {"name": "User"}
                        ]
                    }
                }
            }
        }
    },
    HTTPStatus.FORBIDDEN: {
        "description": "Forbidden action.",
        "content": {
            "application/json": {
                "examples": {
                    "Not Authorized to Assign Role": {
                        "value": {
                            "detail": "You do not have permission to assign this role."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.CONFLICT: {
        "description": "Role already assigned to the user.",
        "content": {
            "application/json": {
                "examples": {
                    "Role Already Assigned": {
                        "value": {
                            "detail": "This role is already assigned to the user."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Role Assignment": {
                        "value": {
                            "detail": "An internal server error occurred while assigning the role."
                        }
                    }
                }
            }
        }
    }
}

detach_role = {
    HTTPStatus.OK: {
        "description": "Role successfully detached from the user.",
        "content": {
            "application/json": {
                "examples": {
                    "Remaining Roles List": {
                        "value": [
                            {"name": "User"}
                        ]
                    }
                }
            }
        }
    },
    HTTPStatus.FORBIDDEN: {
        "description": "Forbidden action.",
        "content": {
            "application/json": {
                "examples": {
                    "Not Authorized to Detach Role": {
                        "value": {
                            "detail": "You do not have permission to detach this role."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Role Detachment": {
                        "value": {
                            "detail": "An internal server error occurred while detaching the role."
                        }
                    }
                }
            }
        }
    }
}

login_oauth = {
    HTTPStatus.FOUND: {
        "description": "Redirect to the OAuth provider's login page.",
        "content": {
            "application/json": {
                "examples": {
                    "Redirect Example": {
                        "value": {
                            "detail": "Redirecting to OAuth provider's login page."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.BAD_REQUEST: {
        "description": "Bad request, possibly due to invalid provider name or errors during redirect.",
        "content": {
            "application/json": {
                "examples": {
                    "Invalid Provider": {
                        "value": {
                            "detail": "Invalid OAuth provider specified."
                        }
                    },
                    "Redirect Failed": {
                        "value": {
                            "detail": "OAuth redirect failed."
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during the OAuth redirect process.",
        "content": {
            "application/json": {
                "examples": {
                    "Server Error on Redirect": {
                        "value": {
                            "detail": "Error getting OAuth provider."
                        }
                    }
                }
            }
        }
    }
}

auth_callback = {
    HTTPStatus.OK: {
        "description": "Successful OAuth authentication. Access and refresh tokens are returned.",
        "content": {
            "application/json": {
                "examples": {
                    "Successful Authentication": {
                        "value": {
                            "access_token": "example_access_token",
                            "refresh_token": "example_refresh_token"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.BAD_REQUEST: {
        "description": "Bad request, possibly due to OAuth authorization errors.",
        "content": {
            "application/json": {
                "examples": {
                    "OAuth Error": {
                        "value": {
                            "detail": "Error message from OAuthError"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during the authentication process.",
        "content": {
            "application/json": {
                "examples": {
                    "Database Error": {
                        "value": {
                            "detail": "User creation failed"
                        }
                    },
                    "Server Error on Authentication": {
                        "value": {
                            "detail": "Error getting OAuth provider"
                        }
                    }
                }
            }
        }
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Unauthorized access, possibly due to invalid token or credentials.",
        "content": {
            "application/json": {
                "examples": {
                    "Invalid Credentials": {
                        "value": {
                            "detail": "Invalid or expired token provided."
                        }
                    }
                }
            }
        }
    }
}
