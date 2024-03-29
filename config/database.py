from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

mongohost = os.getenv("MONGO_HOST")
# print(mongohost)
client = MongoClient(mongohost)

db = client.fyp_db

collection_chat = db["chat_collections"]
collection_user = db["user_collections"]
collection_file = db["file_collections"]
collection_quiz = db["quiz_collections"]
collection_chat_history_doc = db["chat_history_doc_collections"]
