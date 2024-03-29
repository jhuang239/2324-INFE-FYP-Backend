import datetime
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from gpt.gpt import chat
from typing import Annotated
from .auth import get_current_user
from starlette import status
from embedding import file_embedding
from config.database import collection_quiz
from models.models import quiz
from email_func.send_email import send_email

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
def chatwithdoc(user: user_dependency, prompt=Body()):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    chat_history_tuple = []
    for message in prompt['history']:
        chat_history_tuple.append(
            (message['question'], message['answer']))

    print("chat_history", chat_history_tuple)

    response = file_embedding.start_conversation(
        query=prompt['query'],
        pass_in_index_name=user["user_id"].lower(),
        chat_history=chat_history_tuple
    )
    return response

async def generate_question_background(document_name: str, num_questions: int, index_name: str, user: user_dependency):
    response = file_embedding.start_conversation(
        query="Please help to summarize the " + document_name +
        " as detailed as possible, list out the elements of the document, and provide the key points with explanations, exclude the author's information, exclude the page content about Intended Learning Outcomes.",
        pass_in_index_name=index_name)

    answer = response["answer"]
    mcq = file_embedding.generate_mcq_from_document(answer, num_questions)
    mcq = file_embedding.parse_json(mcq.content)

    print (user["email"])

    now = datetime.datetime.now()

    quiz_id = str(uuid.uuid4())
    quiz_name = quiz_id + "_" + now.strftime("%Y-%m-%d %H:%M:%S")
    print(quiz_name)
    quiz_time = now
    quiz_content = mcq

    quiz_data = quiz(user_id=user["user_id"], quiz_id=quiz_id,
                     quiz_name=quiz_name, time=quiz_time, content=quiz_content)
    
    collection_quiz.insert_one(quiz_data.dict())
    print("Quiz generated successfully")
    await send_email("Quiz generated successfully", user["email"], quiz_name)
    print("Email sent successfully")
    return
    


@router.get("/summarize")
def summarize(user: user_dependency, document_name: str, num_questions: int, background_task: BackgroundTasks):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    print(user)

    background_task.add_task(generate_question_background, document_name, num_questions, user["user_id"].lower(), user)
    return {"message": "Summarization and MCQ generation in progress, please check your email for the results."}
