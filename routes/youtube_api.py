from fastapi import APIRouter, Depends, HTTPException
from models.models import youtube_obj
from .auth import get_current_user
from typing import Annotated
from pytube import Search, YouTube
import uuid
from fastapi_sessions.backends.implementations import InMemoryBackend
import json
from embedding.file_embedding import embedding_youtube_video

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
async def generate_quiz(user: user_dependency, url: str):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid authentication credentials")

    embedding_youtube_video(url, user["user_id"])

    return {"message": "Quiz generated successfully!"}
