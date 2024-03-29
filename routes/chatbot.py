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


@router.post("/chatwithdoc")
def chatwithdoc(prompt=Body()):

    chat_history_tuple = []
    for message in prompt['chat_history']:
        chat_history_tuple.append(
            (message['question'], message['chat_history']))

    print("chat_history", chat_history_tuple)

    response = file_embedding.start_conversation(
        query=prompt['query'],
        pass_in_index_name=prompt['index_name'],
        chat_history=chat_history_tuple
    )
    return response


@router.get("/summarize")
def summarize(document_name: str, num_questions: int, index_name: str):
    response = file_embedding.start_conversation(
        query="Please help to summarize the " + document_name +
        " as detailed as possible, list out the elements of the document, and provide the key points with explanations, exclude the author's information, exclude the page content about Intended Learning Outcomes.",
        pass_in_index_name=index_name)

    answer = response["answer"]
    mcq = file_embedding.generate_mcq_from_document(answer, num_questions)
    mcq = file_embedding.parse_json(mcq.content)
    return {"summarization": response, "mcq": mcq}
