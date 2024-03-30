from models.models import chat_history
from config.database import collection_chat_history_doc
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Body
from .auth import get_current_user
from typing import Annotated
from starlette import status
from schemas.schemas import list_serial_history_doc_name


router = APIRouter(
    prefix="/chat_history_doc",
    tags=["chat_history_doc"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


# * API to get chat history doc
@router.get("/chatHistoryDoc")
async def get_chat(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    history = list(collection_chat_history_doc.find({"user_id": user["user_id"]}))
    return list_serial_history_doc_name(history)


# * API to get chat history doc by chat name
@router.get("/get_chat")
async def get_chat(user: user_dependency, id: str):
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    print("id", id)

    history = collection_chat_history_doc.find_one({"_id": ObjectId(id)},{"_id":0})
    return history
    

# * API to add chat history doc
@router.post("/add_chat")
async def add_chat(user: user_dependency, obj=Body()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    obj["user_id"] = user["user_id"]
    result = collection_chat_history_doc.insert_one(dict(obj))
    if (result.acknowledged):
        return {"id": str(result.inserted_id)}
    else:
        return {"error": "insert failed!"}



# * API to update chat history doc
@router.put("/update_chat")
async def update_chat(user: user_dependency, id: str, obj=Body()):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    result = collection_chat_history_doc.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": dict(obj)})
    if (result):
        return {"message": "update success!"}
    else:
        return {"error": "update failed!"}
    

# * API to delete chat history doc
@router.delete("/delete_chat")
async def delete_chat(user: user_dependency, id: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    result = collection_chat_history_doc.delete_one({"_id": ObjectId(id)})
    if (result):
        return {"message": "delete success!"}
    else:
        return {"error": "delete failed!"}