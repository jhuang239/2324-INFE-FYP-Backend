from fastapi import APIRouter
from models.models import user
from config.database import collection_user

router = APIRouter()

# user

@router.get("/")
async def hello():
    return {"message": "Hello World"}