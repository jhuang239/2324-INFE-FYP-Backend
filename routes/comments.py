from config.database import collection_discussion_comment
from models.models import comments
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File
from fastapi.encoders import jsonable_encoder
from .auth import get_current_user
from typing import Annotated, List
from starlette import status
import datetime
from pydantic import BaseModel
from pymongo import ASCENDING
from schemas.schemas import get_file_link
from config.firebaeConfig import bucket
import uuid

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class comment_body(BaseModel):
    discussion_id: str
    detail: str

def checker(data: str = Form(...)):
    try:
        return comment_body.model_validate_json(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


# * API to add a comment
@router.post("/add_comment")
async def add_comment(user: user_dependency, obj: comment_body = Depends(checker), files: List[UploadFile] = File(...)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    file_list = []
    for file in files:
        file_name = str(uuid.uuid4()) + "_" + file.filename
        blob = bucket.blob(file_name)
        blob.upload_from_file(file.file)
        file_list.append(file_name)


    now = datetime.datetime.now()
    comment = comments(discussion_id=obj.discussion_id,
                       user_id=user["user_id"], author=user["name"], detail=obj.detail, files=file_list, created_at=now, updated_at=now)

    result = collection_discussion_comment.insert_one(comment.dict())
    if result.acknowledged:
        return {"message": str(result.inserted_id)}
    else:
        return {"message": "Failed to add comment"}


# * API to get all comments by discussion_id
@router.get("/get_comments")
async def get_comments(user: user_dependency, discussion_id: str):
    results = list(collection_discussion_comment.find(
        {"discussion_id": discussion_id}, {"_id": 0}).sort("created_at", ASCENDING))

    # result["files"] = [get_file_link(file) for file in result["files"]]

    for result in results:
        result["files"] = [get_file_link(file) for file in result["files"]]

    print(results)

    if result:
        return result
    else:
        return {"message": "No comments found for this discussion"}
