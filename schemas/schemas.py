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
