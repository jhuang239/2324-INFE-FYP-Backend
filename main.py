from fastapi import FastAPI
from routes import chat_history, user, chatbot, auth

app = FastAPI()
app.include_router(chat_history.router)
app.include_router(user.router)
app.include_router(chatbot.router)
app.include_router(auth.router)