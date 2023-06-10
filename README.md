# Project Readme

This is a sample project that demonstrates the usage of several concepts including Pydantic, SQLAlchemy ORM, and JWT authentication in a FastAPI application.

## Requirements

To run this project, you need to have the following dependencies installed:

- Python 3.7 or above
- FastAPI
- SQLAlchemy
- Pydantic
- Passlib
- PyJWT

You can install the dependencies by running the following command:

pip install fastapi sqlalchemy pydantic passlib pyjwt


## Configuration

Before running the application, you need to configure the MySQL database connection. Open the file `main.py` and find the following line:

```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mypassword@localhost/findProjects"
```

Replace `root` with your MySQL `username`, mypassword with your MySQL password, and `findProjects` with the name of your database.

You also need to set your own secret key for JWT token encoding. Locate the line:
```
SECRET_KEY = "my-secret-key"  # Change this to your own secret key
```

Replace "my-secret-key" with your desired secret key.

## the Application
To run the application, execute the following command in your terminal:
```
uvicorn main:app --reload
```

This will start the FastAPI development server, and the application will be accessible at `http://localhost:8000`.

# API Endpoints
## Register User
- URL: `/register`
- Method: POST
Description: Register a new user.
Request Body:
username (string): The username of the user.
email (string): The email address of the user.
password (string): The password of the user.
Response:
message (string): A success message.
access_token (object): An access token object containing the generated access token and token type.
Login User
URL: /login
Method: POST
Description: Log in an existing user.
Request Body:
username (string): The username of the user.
password (string): The password of the user.
Response:
message (string): A success message.
access_token (object): An access token object containing the generated access token and token type.
Create Project
URL: /projects
Method: POST
Description: Create a new project.
Authorization: Bearer token (obtained from login or register)
Request Body:
title (string): The title of the project.
description (string): The description of the project.
Response:
Returns the created project object.
Get Project
URL: /projects/{project_id}
Method: GET
Description: Get details of a specific project.
Authorization: Bearer token (obtained from login or register)
Path Parameters:
project_id (integer): The ID of the project.
Response:
Returns the project object if found.
Delete Project
URL: /projects/{project_id}
Method: DELETE
Description: Delete a specific project.
Authorization: Bearer token (obtained from login or
