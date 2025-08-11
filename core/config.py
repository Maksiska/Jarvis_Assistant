import os
from dotenv import load_dotenv

# Загружаем переменные из .env в окружение
load_dotenv()

# === Модель и Ollama ===
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:3000")

# === ChromaDB ===
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "commands")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chromadb")

# === Интерфейс ===
USE_TAIPY_UI = os.getenv("USE_TAIPY_UI", "false").lower() == "true"
WEB_PORT = int(os.getenv("WEB_PORT", 5000))

# === Озвучка ===
TTS_VOICE_RATE = int(os.getenv("TTS_VOICE_RATE", 130))
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "ru")

# === Прочее ===
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

SETTINGS = {
    "OLLAMA_MODEL": OLLAMA_MODEL,
    "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
    "CHROMA_COLLECTION_NAME": CHROMA_COLLECTION_NAME,
    "CHROMA_PERSIST_DIR": CHROMA_PERSIST_DIR,
    "USE_TAIPY_UI": USE_TAIPY_UI,
    "WEB_PORT": WEB_PORT,
    "TTS_VOICE_RATE": TTS_VOICE_RATE,
    "TTS_LANGUAGE": TTS_LANGUAGE,
    "DEBUG_MODE": DEBUG_MODE,
}
