from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models.models import user
from config.database import collection_user
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError
from starlette import status


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = '9bfe11f429a92e93b54e15381285f267fd060052984e13bc5894648777933d3b'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str

def authenticate_user(username: str, password: str):
    user = collection_user.find_one({"user_id": username})
    print(user)
    if(not user):
        return False
    if(not bcrypt_context.verify(password, user["password"])):
        return False
    return user

def create_access_token(name: str, user_id: str, email: str, expires_delta: timedelta):
    encode = {"sub": name, "id": user_id, "email": email}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        user_id: str = payload.get("id")
        email: str = payload.get("email")
        if name is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return {"name": name, "user_id": user_id, "email": email}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

@router.post("/add_user")
async def post_user(user: user):
    newUser = dict(user)
    newUser["activated"] = False
    encrypted_password = bcrypt_context.hash(newUser["password"])
    print(encrypted_password)
    newUser["password"] = encrypted_password
    result = collection_user.insert_one(newUser)
    if(result.acknowledged):
        return {"id": str(result.inserted_id)}
    else:
        return {"error": "insert failed!"}
    

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if(not user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    token = create_access_token(user["name"], user["user_id"], user['email'], timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}