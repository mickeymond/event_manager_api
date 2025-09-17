from fastapi import Form, File, UploadFile, HTTPException, status, APIRouter, Depends
from db import events_collection
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import date, time

# Create events router
events_router = APIRouter()


# Events endpoints
@events_router.get("/events")
def get_events(title="", description="", limit=10, skip=0):
    # Get all events from database
    events = events_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}},
                {"description": {"$regex": description, "$options": "i"}},
            ]
        },
        limit=int(limit),
        skip=int(skip),
    ).to_list()
    # Return response
    return {"data": list(map(replace_mongo_id, events))}


@events_router.post("/events")
def post_event(
    title: Annotated[str, Form()],
    venue: Annotated[str, Form()],
    start_time: Annotated[time, Form()],
    end_time: Annotated[time, Form()],
    start_date: Annotated[date, Form()],
    end_date: Annotated[date, Form()],
    image: Annotated[UploadFile, File()],
    description: Annotated[str, Form()],
    # credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
):
    # print(credentials)
    # Upload image to cloudinary to get a url
    upload_result = cloudinary.uploader.upload(image.file)
    # Insert event into database
    events_collection.insert_one(
        {
            "title": title,
            "venue": venue,
            "start_time": start_time,
            "end_time": end_time,
            "start_date": start_date,
            "end_date": end_date,
            "image": upload_result["secure_url"],
            "description": description,
        }
    )
    # Return response
    return {"message": "Event added successfully"}


@events_router.get("/events/{event_id}")
def get_event_by_id(event_id):
    # Check if event id is valid
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    # Get event from database by id
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    # Return response
    return {"data": replace_mongo_id(event)}


@events_router.put("/events/{event_id}")
def replace_event(
    event_id,
    title: Annotated[str, Form()],
    venue: Annotated[str, Form()],
    start_time: Annotated[time, Form()],
    end_time: Annotated[time, Form()],
    start_date: Annotated[date, Form()],
    end_date: Annotated[date, Form()],
    image: Annotated[UploadFile, File()],
    description: Annotated[str, Form()],
):
    # Check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    # Upload image to cloudinary to get a url
    upload_result = cloudinary.uploader.upload(image.file)
    # Replace event in database
    events_collection.replace_one(
        filter={"_id": ObjectId(event_id)},
        replacement={
            "title": title,
            "venue": venue,
            "start_time": start_time,
            "end_time": end_time,
            "start_date": start_date,
            "end_date": end_date,
            "image": upload_result["secure_url"],
            "description": description,
        },
    )
    # Return reponse
    return {"message": "Event replaced successfully"}


@events_router.delete("/events/{event_id}")
def delete_event(event_id):
    # Check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid mongo id received!"
        )
    # Delete event from database
    delete_result = events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No event found to delete!")
    # Return response
    return {"message": "Event deleted successfully!"}
