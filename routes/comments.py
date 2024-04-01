from config.database import collection_discussion_comment
from models.models import comments
from fastapi import APIRouter, Depends, HTTPException, Body
from .auth import get_current_user
from typing import Annotated, List
from starlette import status
import datetime
from pydantic import BaseModel
from pymongo import ASCENDING


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class comment_body(BaseModel):
    discussion_id: str
    detail: str


# * API to add a comment
@router.post("/add_comment")
async def add_comment(user: user_dependency, obj: comment_body = Body()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    now = datetime.datetime.now()
    comment = comments(discussion_id=obj.discussion_id,
                       user_id=user["user_id"], author=user["name"], detail=obj.detail, created_at=now, updated_at=now)

    result = collection_discussion_comment.insert_one(comment.dict())
    if result.acknowledged:
        return {"message": str(result.inserted_id)}
    else:
        return {"message": "Failed to add comment"}


# * API to get all comments by discussion_id
@router.get("/get_comments")
async def get_comments(user: user_dependency, discussion_id: str):
    result = list(collection_discussion_comment.find(
        {"discussion_id": discussion_id}, {"_id": 0}).sort("created_at", ASCENDING))

    if result:
        return result
    else:
        return {"message": "No comments found for this discussion"}
