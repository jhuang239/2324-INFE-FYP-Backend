from fastapi import APIRouter, Body, Depends, HTTPException
from gpt.gpt import chat
from typing import Annotated
from .auth import get_current_user
from starlette import status
from embedding import file_embedding

router = APIRouter(
    prefix="/chatbot",
    tags=["chatbot"],
)
user_dependency = Annotated[dict, Depends(get_current_user)]


# chatbot
@router.post("/chatting")
async def chatbot(user: user_dependency, promt=Body()):
    print(promt)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    response = await chat(list(promt))
    return response


@router.get("/chatwithdoc")
async def chatwithdoc():
    response = file_embedding.start_conversation(
        query="what is the difference between interface and abstract class in JAVA?")
    return response
