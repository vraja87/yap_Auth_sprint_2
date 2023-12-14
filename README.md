# Async API

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/telemachor/Auth_sprint_2)
  
## Setup
  
- Create and fill out a `.env` using `.env.example`.
- **Start Docker Containers**: Simply run the `make` command to start all necessary containers and initialize the project:
  - Build and start all Docker services defined in `docker-compose.yaml`.
  - Apply database migrations to set up your database schema.
  - Collect static files for the admin panel.
  - Create a superuser for admin access.
  - Generate initial data for the application (e.g., sample movies, genres, etc.).

## Description
This project provides an admin panel and API for searching and retrieving information about movies, genres, and persons. 

You can filter movies based on various parameters such as genre, IMDb rating, and sorting. Pagination is also supported for easy viewing of large data sets.

# Usage Guide

The Makefile provides a set of commands to manage and interact with project using Docker Compose.  Here's how you can use them:

#### Base Makefile Commands

| Command          | Description                                                                          |
|------------------|--------------------------------------------------------------------------------------|
| `make`           | Initialize the project (start, migrations, create superuser, data generation, etc.). |
| `make up`        | Start all Docker containers in the background.                                       |
| `make down`      | Stop all Docker containers.                                                          |
| `make hard_down` | Remove all Docker containers and networks. Deletes initialization flag.              |
| `make migrate`   | Apply database migrations.                                                           |

#### Running Tests

To run functional tests, execute the following command:

```bash
make test
```


#### Content interaction

> For more details on the API, refer to the Swagger documentation at `/api/openapi-movies`

- **GET /api/v1/films/**: Retrieve a list of films with the option to filter by genre, IMDb rating, etc.
- **GET /api/v1/films/search/**: Search for films with optional filtering and "soft" search.
- **GET /api/v1/films/{film_id}**: Retrieve detailed information about a film by its ID.
- **GET /api/v1/genres/**: Retrieve a list of all genres.
- **GET /api/v1/persons/search/**: Search for persons by name with optional "soft" search.


### Role Management

> For more details on the API, refer to the Swagger documentation at `/api/openapi-auth`

- **POST /api/v1/roles/create**: Creates a new role.
- **DELETE /api/v1/roles/delete/{role_id}**: Deletes a role based on its UUID.
- **GET /api/v1/roles/**: Retrieves a list of all roles.
- **GET /api/v1/roles/{role_id}**: Fetches details of a role by its UUID.
- **GET /api/v1/roles/{role_name}/name**: Fetches details of a role by its name.
- **GET /api/v1/roles/user/{user_id}**: Returns the roles assigned to a user.
- **POST /api/v1/roles/assign**: Assigns a role to a user.
- **DELETE /api/v1/roles/detach**: Detaches a role from a user.

### User Management

- **POST /api/v1/users/signup**: Registers a new user.
- **POST /api/v1/users/login**: Authenticates a user and provides access tokens.
- **POST /api/v1/users/logout**: Logs out a user from the current session.
- **POST /api/v1/users/logout_all**: Logs out a user from all sessions.
- **POST /api/v1/users/refresh**: Refreshes a user's tokens.
- **GET /api/v1/users/login-history**: Retrieves a user's login history.
- **PATCH /api/v1/users/update**: Updates user information.
- **GET /api/v1/users/access-roles**: Retrieves the roles of the current user.
- **GET /login/{provider}**: Initiates the OAuth login process for a specified provider. 
This endpoint supports authentication through various OAuth providers, including Yandex and Google.
