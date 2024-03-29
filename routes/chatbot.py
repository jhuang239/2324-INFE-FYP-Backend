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
def chatwithdoc(query: str):
    response = file_embedding.start_conversation(
        query=query,
        pass_in_index_name="kim1118")
    return response


@router.get("/summarize")
def summarize(document_name: str, num_questions: int):
    response = file_embedding.start_conversation(
        query="Please help to summarize the " + document_name +
        " as detailed as possible, list out the elements of the document, and provide the key points with explanations, not need to include the information of author and date.",
        pass_in_index_name="kim1118")

    answer = response["answer"]
    mcq = file_embedding.generate_mcq_from_document(answer, num_questions)
    mcq = file_embedding.parse_json(mcq.content)
    return {"summarization": response, "mcq": mcq}
