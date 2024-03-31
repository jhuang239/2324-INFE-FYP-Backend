from models.models import quiz
from config.database import collection_quiz
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Body
from .auth import get_current_user
from typing import Annotated
from starlette import status
from schemas.schemas import list_serial_quiz


router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]

# * API to get all quiz by user_id
@router.get("/get_all_quiz")
async def get_all_quiz(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    quizzes = list(collection_quiz.find({"user_id": user["user_id"]}, {"_id": 0}))
    return list_serial_quiz(quizzes)


# API to get quiz by quiz_id
@router.get("/get_quiz")
async def get_quiz(user: user_dependency, quiz_id: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    quiz = collection_quiz.find_one({"quiz_id": quiz_id}, {"_id": 0})
    return quiz


# * API to put quiz
@router.put("/put_quiz")
async def put_quiz(user: user_dependency, quiz_id: str, obj=Body()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    obj["user_id"] = user["user_id"]
    result = collection_quiz.find_one_and_update({"quiz_id": quiz_id}, {"$set": dict(obj)})
    if (result):
        return {"success": "update success!"}
    else:
        return {"error": "insert failed!"}