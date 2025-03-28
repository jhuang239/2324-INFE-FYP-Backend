from models.models import chat_history
from config.database import collection_chat
from schemas.schemas import list_serial, list_serial_message
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Body
from .auth import get_current_user
from typing import Annotated
from starlette import status


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)
user_dependency = Annotated[dict, Depends(get_current_user)]


# chat_history
# @router.get("/chatHistory")
# async def get_chat():
#     history = list_serial(collection_chat.find())
#     return history


@router.get("/get_chat")
async def get_chat(id: str, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    print(user)
    histories_list = []
    histories = collection_chat.find_one({"_id": ObjectId(id)},{"_id":0})
    print(histories)
    if (histories):
        histories_list.append(histories)
        return histories_list


@router.post("/add_chat")
async def post_history(user: user_dependency, passIn_history=Body()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    passIn_history["user_id"] = user["user_id"]
    result = collection_chat.insert_one(dict(passIn_history))
    if (result.acknowledged):
        return {"id": str(result.inserted_id)}
    else:
        return {"error": "insert failed!"}


@router.put("/update_chat")
async def update_chat(user: user_dependency, id: str, history=Body()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    result = collection_chat.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": dict(history)})
    if (result):
        return {"id": str(result["_id"])}
    else:
        return {"error": "update failed!"}


@router.delete("/delete_chat")
async def delete_chat(user: user_dependency, id: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    result = collection_chat.find_one_and_delete({"_id": ObjectId(id)})
    if (result):
        return {"id": str(result["_id"])}
    else:
        return {"error": "delete failed!"}


@router.get("/get_all_chat")
async def get_all_chat(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    histories = list(collection_chat.find({"user_id": user["user_id"]}))
    if (histories):
        return list_serial(histories)
    else:
        return {"error": "not found!"}
