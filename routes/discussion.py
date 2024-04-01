from models.models import discussion_schema
from config.database import collection_discussion
from schemas.schemas import list_serial_discussion
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File
from fastapi.encoders import jsonable_encoder
from .auth import get_current_user
from typing import Annotated, List
from starlette import status
from bson import ObjectId
from pydantic import BaseModel
from config.firebaeConfig import bucket
import datetime
import uuid
from pymongo import DESCENDING
import re

router = APIRouter(
    prefix="/discussion",
    tags=["discussion"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class discussion_body(BaseModel):
    topic: str
    category: str
    description: str


def checker(data: str = Form(...)):
    try:
        return discussion_body.model_validate_json(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


# * API to add a discussion
@router.post("/add_discussion")
async def add_discussion(user: user_dependency, obj: discussion_body = Depends(checker), files: List[UploadFile] = File(...), banner_img: UploadFile = File(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    print(obj.topic)
    print(obj.category)
    print(obj.description)
    for file in files:
        print(file.filename)
    print(banner_img.filename)

    banner_img_name = str(uuid.uuid4()) + "_" + banner_img.filename
    banner_blob = bucket.blob(banner_img_name)
    banner_blob.upload_from_file(banner_img.file)

    file_list = []

    for file in files:
        file_name = str(uuid.uuid4()) + "_" + file.filename
        blob = bucket.blob(file_name)
        blob.upload_from_file(file.file)
        file_list.append(file_name)

    now = datetime.datetime.now()

    discussion = discussion_schema(user_id=user["user_id"], author=user["name"], topic=obj.topic, category=obj.category,
                                   created_at=now, updated_at=now, banner_img=banner_img_name, files=file_list, description=obj.description)

    print(discussion.dict())
    result = collection_discussion.insert_one(discussion.dict())
    if (result.acknowledged):
        return {"id": str(result.inserted_id)}
    else:
        return {"error": "insert failed!"}


# API to get a discussion
@router.get("/get_discussion")
async def get_discussion(id: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    discussion = collection_discussion.find_one(
        {"_id": ObjectId(id)}, {"_id": 0})

    if (discussion):
        discussion["id"] = id
        return discussion
    else:
        return {"error": "discussion not found!"}


# API to get all discussions
@router.get("/get_all_discussions")
async def get_all_discussions(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    discussions = list(collection_discussion.find().sort(
        "updated_at", DESCENDING).limit(20))
    if (discussions):
        return list_serial_discussion(discussions)
    else:
        return {"error": "not found!"}


# * API to get discussions by category
@router.get("/get_discussion_by_category")
async def get_discussion_by_category(category: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    discussions = list(collection_discussion.find(
        {"category": category}).sort("updated_at", DESCENDING).limit(20))
    if (discussions):
        return list_serial_discussion(discussions)
    else:
        return {"error": "not found!"}


@router.get("/get_discussion_by_topic")
async def get_discussion_by_topic(topic: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    search_term = topic
    pattern = re.compile(f'.*{re.escape(search_term)}.*', re.IGNORECASE)

    query = {"topic": {"$regex": pattern}}

    discussions = list(collection_discussion.find(
        query).sort("updated_at", DESCENDING).limit(20))
    if (discussions):
        return list_serial_discussion(discussions)
    else:
        return {"error": "not found!"}
