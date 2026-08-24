# Stores language preference per user
user_language = {}  # { user_id: "English" / "Hindi" / "Bengali" }


def set_language(user_id: str, lang: str):
    user_language[user_id] = lang


def get_language(user_id: str) -> str:
    return user_language.get(user_id, "English")  # default English


def clear_language(user_id: str):
    if user_id in user_language:
        del user_language[user_id]