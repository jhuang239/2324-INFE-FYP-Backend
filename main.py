from fastapi import FastAPI
from routes import chat_history, user, chatbot, auth, file_storage, chat_history_doc, quiz, discussion

app = FastAPI()
app.include_router(chat_history.router)
app.include_router(user.router)
app.include_router(chatbot.router)
app.include_router(auth.router)
app.include_router(file_storage.router)
app.include_router(chat_history_doc.router)
app.include_router(quiz.router)
app.include_router(discussion.router)