import datetime
import os
from config.firebaeConfig import cred
from firebase_admin import storage, initialize_app
from fastapi import File, UploadFile, APIRouter, Depends, HTTPException, Body
from .auth import get_current_user
from typing import Annotated
from starlette import status
from models.models import file_structure
from config.database import collection_file
from embedding import file_embedding
import uuid

router = APIRouter(
    prefix="/file",
    tags=["file"],
)
user_dependency = Annotated[dict, Depends(get_current_user)]

initialize_app(cred, {'storageBucket': 'fyp-file-storage.appspot.com'})
bucket = storage.bucket()


# * API to create a folder
@router.post("/createFolder")
async def create_folder(user: user_dependency, passIn_object=Body()):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    folder_id = str(uuid.uuid4())
    folder_type = "folder"
    folder_name = passIn_object["name"]
    parent_id = passIn_object["parent_id"]
    print(folder_id)
    folder = file_structure(id=folder_id, user_id=user["user_id"],
                            name=folder_name, parent_id=parent_id, type=folder_type, updated_at=datetime.datetime.now(), created_at=datetime.datetime.now())
    collection_file.insert_one(folder.dict())
    return {"message": "Folder created successfully"}


# * API to get all folders based on parent_id
@router.get("/getFolders")
async def get_folders(user: user_dependency, parent_id: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    folders = collection_file.find(
        {"user_id": user["user_id"], "parent_id": parent_id, "type": "folder"}, {"_id": 0})
    folder_list = []
    for folder in folders:
        folder_list.append(folder)
    return {"message": "Folders retrieved successfully", "folders": folder_list}


@router.get("/getFilesAndFolders")
async def get_files_and_folders(user: user_dependency, parent_id: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    files = collection_file.find(
        {"user_id": user["user_id"], "parent_id": parent_id}, {"_id": 0})
    file_list = []
    for file in files:
        file_list.append(file)
    return {"message": "Files retrieved successfully", "files": file_list}


# * API to upload a file
@router.post("/upload")
async def upload_file(user: user_dependency, parent_id: str, file: UploadFile = File(...)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    file_id = str(uuid.uuid4())
    file_name = file_id+"_"+file.filename
    file_type = "file"
    file_obj = file_structure(id=file_id, user_id=user["user_id"],
                              name=file_name, parent_id=parent_id, type=file_type,updated_at=datetime.datetime.now(), created_at=datetime.datetime.now())
    collection_file.insert_one(file_obj.dict())

    file_bytes = await file.read()
    blob = bucket.blob(file_name)
    blob.upload_from_string(file_bytes, content_type=file.content_type)

    return {"message": "File uploaded successfully"}


# * API to get file url for 7 days
@router.get("/getPath")
async def get_path(user: user_dependency, file_name: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    blob = bucket.blob(file_name)
    download_url = blob.generate_signed_url(
        datetime.timedelta(days=7), method='GET')
    print(download_url)
    return {"message": "File downloaded successfully", "download_url": download_url}


# * API to download a file in local storage
@router.get("/download")
async def download_file(user: user_dependency, file_name: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    filePath = f"temp/{file_name}"
    blob = bucket.blob(file_name)
    blob.download_to_filename(filePath)
    return {"message": "File downloaded successfully", "file_path": filePath}


# * API to download all files in a folder
@router.get("/downloadFolder")
async def download_folder(user: user_dependency, folder_id: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    user_id = user["user_id"]

    os.makedirs(f"temp/{user_id}", exist_ok=True)
    _files = get_files_in_folder(folder_id, user["user_id"], [])
    for file in _files:
        blob = bucket.blob(file["name"])
        blob.download_to_filename(f"temp/{user_id}/{file['name']}")

    file_embedding.handle_file_embedding(
        f"temp/{user_id}", user["user_id"].lower())

    return {"message": "Files downloaded successfully", "files": _files}


# * API to list all files
@router.get("/list")
async def list_files(user: user_dependency):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    files = bucket.list_blobs()
    file_list = []
    for file in files:
        file_list.append(file.name)
    return {"message": "Files retrieved successfully", "files": file_list}


# * API to delete a file
@router.delete("/delete")
async def delete_file(user: user_dependency, file_name: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    blob = bucket.blob(file_name)
    blob.delete()
    collection_file.delete_one({"name": file_name})
    return {"message": "File deleted successfully"}


# * API to delete a folder
@router.delete("/deleteFolder")
async def delete_folder(user: user_dependency, folder_id: str):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")

    message = delete_sub_folders_and_files(folder_id, user["user_id"])
    return message


# * Function to delete sub folders and files
def delete_sub_folders_and_files(parent_id, user_id):
    sub_folders = collection_file.find(
        {"parent_id": parent_id, "user_id": user_id}, {"_id": 0})
    for sub_folder in sub_folders:
        print(sub_folder["name"])
        delete_sub_folders_and_files(sub_folder["id"], user_id)
    collection_file.delete_one({"id": parent_id})
    collection_file.delete_many({"parent_id": parent_id})
    bucket.delete_blobs(blobs=list(bucket.list_blobs(prefix=parent_id)))
    return {"message": "Folder deleted successfully"}


# * Function to get all files in a folder
def get_files_in_folder(parent_id, user_id, _files):
    files = collection_file.find(
        {"parent_id": parent_id, "user_id": user_id}, {"_id": 0})
    for file in files:
        if (file["type"] == "folder"):
            get_files_in_folder(file["id"], user_id, _files)
        else:
            _files.append(file)
    return _files
