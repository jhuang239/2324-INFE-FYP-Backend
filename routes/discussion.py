from models.models import discussion_schema, comments
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
import uuid

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

    banner_img_name = str(uuid.uuid4()) + banner_img.filename
    banner_blob = bucket.blob(banner_img_name)
    banner_blob.upload_from_file(banner_img.file)
    
    file_list = []

    for file in files:
        file_name = str(uuid.uuid4()) + file.filename
        blob = bucket.blob(file_name)
        blob.upload_from_file(file.file)
        file_list.append(file_name)

    discussion = discussion_schema(user_id=user["user_id"], author=user["name"], topic=obj.topic, category=obj.category, description=obj.description, banner_img=banner_img_name, file=file_list)

    print (discussion.dict())


    return {"message": "success"}