from enum import Enum
from fastapi import APIRouter, Form, status, HTTPException
from typing import Annotated
from pydantic import EmailStr
from db import users_collection
import bcrypt
import jwt
import os


class UserRole(str, Enum):
    VENDOR = "vendor"
    CUSTOMER = "customer"


# Create users router
users_router = APIRouter(tags=["Users"])


# Define endpoints
@users_router.post("/users/register")
def register_user(
    username: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    role: Annotated[UserRole, Form()] = UserRole.CUSTOMER,
):
    # Ensure user does not exist
    user_count = users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "User already exist!")
    # Hash user password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    # Save user into database
    users_collection.insert_one(
        {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
        }
    )
    # Return response
    return {"message": "User registered successfully!"}


@users_router.post("/users/login")
def login_user(
    email: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
):
    # Ensure user exist
    user = users_collection.find_one(filter={"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist!")
    # Compare their password
    correct_password = bcrypt.checkpw(password.encode(), user["password"])
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials!")
    # Generate for them an access token
    encoded_jwt = jwt.encode(
        {"id": str(user["_id"])}, os.getenv("JWT_SECRET_KEY"), "HS256"
    )
    # Return reponse
    return {"message": "User logged in successfully!", "access_token": encoded_jwt}
