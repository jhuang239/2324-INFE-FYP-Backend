import datetime
from config.firebaeConfig import cred;
from firebase_admin import storage, initialize_app
from fastapi import File, UploadFile, APIRouter, Depends, HTTPException, Body
from .auth import get_current_user
from typing import Annotated
from starlette import status

router = APIRouter(
    prefix="/file",
    tags=["file"],
)
user_dependency = Annotated[dict, Depends(get_current_user)]

initialize_app(cred, {'storageBucket': 'fyp-file-storage.appspot.com'})
bucket = storage.bucket()

@router.post("/upload")
async def upload_file(
    # user: user_dependency, 
    fileName: str, file: UploadFile = File(...)):
    file_bytes = await file.read()

    # Upload the file to Firebase Storage
    blob = bucket.blob(file.filename)
    blob.upload_from_string(file_bytes, content_type=file.content_type)
    download_url = blob.public_url
    print(download_url)
    return {"message": "File uploaded successfully", "download_url": download_url}

@router.get("/download/{file_name}")
async def download_file(file_name: str):
    blob = bucket.blob(file_name)
    download_url = blob.public_url
    print(download_url)
    return {"message": "File downloaded successfully", "download_url": download_url}