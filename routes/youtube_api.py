from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from models.models import youtube_obj, quiz
from config.database import collection_quiz
from .auth import get_current_user
from typing import Annotated
from pytube import Search, YouTube
import uuid
from fastapi_sessions.backends.implementations import InMemoryBackend
import json
from embedding.file_embedding import embedding_youtube_video, generate_mcq_from_document, parse_json
from email_func.send_email import send_email_background
import datetime

router = APIRouter(
    prefix="/yt",
    tags=["youtube api"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


# * API to search youtube videos
@router.get("/search")
async def search_youtube(user: user_dependency, query: str, page: int = 1):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid authentication credentials")

    print(page)

    search = Search(query)
    search_results = search.results
    result = []
    youtube_videos = []
    if (page > 1):
        for x in range(1, page - 1):
            print("hello")
            search.get_next_results()
            search_results = search.results

        temp1 = []
        for x in range(len(search.results)):
            temp1.append(search.results[x])

        search.get_next_results()
        temp2 = []
        for x in range(len(search.results)):
            temp2.append(search.results[x])

        print("temp1", len(temp1))
        print("temp2", len(temp2))
        result = [x for x in temp2 if x not in temp1]
    else:
        result = search_results

    print("search_result", len(search_results))
    print("result", len(result))

    for video in result:
        youtube_videos.append(youtube_obj(
            url=video.watch_url,
            thumbnail=video.thumbnail_url,
            title=video.title,
            author=video.author,
            views=video.views,
            length=video.length,
            publish_date=video.publish_date
        ))

    print(youtube_videos)
    print("youtube_videos", len(youtube_videos))
    return {"video_list": youtube_videos}


# * API to get youtube video details
@router.get("/get_video")
async def get_video(user: user_dependency, url: str):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid authentication credentials")

    yt = YouTube(url)
    obj = {
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
        "author": yt.author,
        "views": yt.views,
        "length": yt.length,
        "publish_date": yt.publish_date,
        "description": yt.description,
        "metadata": yt.metadata,
    }

    return obj


# * API to generate quiz from youtube video
@router.get("/generate_quiz")
async def generate_quiz(user: user_dependency, url: str, num_question: int, background_tasks: BackgroundTasks):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid authentication credentials")

    yt = YouTube(url)

    quiz_id = str(uuid.uuid4())
    quiz_name = "Quiz from Youtube video: " + yt.title
    background_tasks.add_task(
        background_embedding_youtube_video, url, user["user_id"], quiz_id, quiz_name, num_question)
    send_email_background(background_tasks=background_tasks, subject="Quiz generated successfully",
                          email_to=user["email"], quiz_name=quiz_name, type="quiz")

    return {"message": "Quiz generated successfully, please check your email for the results."}


def background_embedding_youtube_video(video_url: str, user_id: str, quiz_id: str, quiz_name: str, num_questions: int):

    docs = embedding_youtube_video(video_url, user_id)
    mcq = generate_mcq_from_document(docs[0].page_content, num_questions)
    mcq = parse_json(mcq.content)
    now = datetime.datetime.now()
    quiz_time = now
    quiz_content = []
    for question in mcq:
        q = dict()
        q["question"] = question["question"]
        options = []
        options.append(question["option_1"])
        options.append(question["option_2"])
        options.append(question["option_3"])
        options.append(question["option_4"])
        q["options"] = options
        q["answer"] = question["answer"]
        quiz_content.append(q)

    print("quiz_content", quiz_content)

    quiz_data = quiz(user_id=user_id, quiz_id=quiz_id, quiz_name=quiz_name,
                     created_at=quiz_time, updated_at=quiz_time, content=quiz_content, completed=False)

    collection_quiz.insert_one(quiz_data.dict())
    print("Quiz generated successfully")
    return
