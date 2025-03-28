from config.firebaeConfig import bucket
import datetime


def get_file_link(file_name):
    blob = bucket.blob(file_name)
    link = blob.generate_signed_url(datetime.timedelta(days=7), method='GET')
    return {"link": link, "file_name": file_name}


def individual_serial(history) -> dict:
    return {
        "id": str(history["_id"]),
        "user_id": history["user_id"],
        "chat_name": history["chat_name"],
        # "time": history["time"],
        # "message": history["message"],
    }


def list_serial(histories) -> list:
    return [individual_serial(history) for history in histories]


def individual_serial_message(history) -> dict:
    return {
        "id": str(history["_id"]),
        "user_id": history["user_id"],
        "chat_name": history["chat_name"],
        "time": history["time"],
        "message": history["message"],
    }


def list_serial_message(histories) -> list:
    return [individual_serial_message(history) for history in histories]


def individual_serial_history_doc_name(history) -> dict:
    return {
        "id": str(history["_id"]),
        "user_id": history["user_id"],
        "chat_name": history["chat_name"],
        "time": history["time"]
    }


def list_serial_history_doc_name(histories) -> list:
    return [individual_serial_history_doc_name(history) for history in histories]


def individual_serial_history_doc(history) -> dict:
    return {
        "id": str(history["_id"]),
        "user_id": history["user_id"],
        "chat_name": history["chat_name"],
        "time": history["time"],
        "message": history["message"],
    }


def list_serial_history_doc(histories) -> list:
    return [individual_serial_history_doc(history) for history in histories]


def individual_serial_quiz(quiz) -> dict:
    return {
        "user_id": quiz["user_id"],
        "quiz_id": str(quiz["quiz_id"]),
        "quiz_name": quiz["quiz_name"],
        "created_at": quiz["created_at"],
        "updated_at": quiz["updated_at"],
        "completed": quiz["completed"],
    }


def list_serial_quiz(quizzes) -> list:
    return [individual_serial_quiz(quiz) for quiz in quizzes]


def individual_serial_discussion(discussion) -> dict:
    return {
        "id": str(discussion["_id"]),
        "author": discussion["author"],
        "topic": discussion["topic"],
        "banner_img": get_file_link(discussion["banner_img"]),
        "category": discussion["category"],
        "created_at": discussion["created_at"],
    }


def list_serial_discussion(discussions) -> list:
    return [individual_serial_discussion(discussion) for discussion in discussions]


def get_user(user) -> dict:
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
        "phone": user["phone"],
        "birthday": user["birthday"],
    }


def get_all_user(users) -> list:
    return [get_user(user) for user in users]
