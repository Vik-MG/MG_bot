# core/utils/locales.py
import json
import os

LOCALIZATION_FILE = "locales.json"
USER_LANG_FILE = "user_languages.json"

# Загружаем локализации
with open(LOCALIZATION_FILE, "r", encoding="utf-8") as file:
    LOCALIZATION = json.load(file)

def get_text(user_lang, key):
    """Получает текст из локализации, если ключ найден, иначе возвращает сам ключ."""
    return LOCALIZATION.get(user_lang, {}).get(key, key)

def load_user_languages():
    """Загружает сохраненные языковые настройки пользователей."""
    if not os.path.exists(USER_LANG_FILE):
        return {}
    with open(USER_LANG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_user_language(user_id, lang):
    """Сохраняет язык пользователя в JSON-файл."""
    data = load_user_languages()
    data[str(user_id)] = lang
    with open(USER_LANG_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
