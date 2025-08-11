import json
import os
from utils.constants import ROLE_USER, ROLE_BOT

# Путь для хранения истории (опционально)
MEMORY_FILE = "conversation_history.json"

# История сессии (в памяти)
dialog_history = []

def add_message(role: str, content: str):
    """
    Добавляет сообщение в историю диалога.

    :param role: 'user' или 'bot'
    :param content: текст сообщения
    """
    message = {"role": role, "content": content}
    dialog_history.append(message)

def get_last_messages(n: int = 5) -> list:
    """
    Возвращает последние n сообщений для контекста.
    """
    return dialog_history[-n:]

def clear_history():
    """
    Очищает историю в памяти и на диске.
    """
    dialog_history.clear()
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

def save_to_file():
    """
    Сохраняет текущую историю в JSON-файл.
    """
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(dialog_history, f, ensure_ascii=False, indent=2)

def load_from_file():
    """
    Загружает историю из файла (если существует).
    """
    global dialog_history
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            dialog_history = json.load(f)
