import pyttsx3
import os
from dotenv import load_dotenv

load_dotenv()

# Получаем скорость речи из .env
TTS_RATE = int(os.getenv("TTS_RATE", 175))

# Инициализируем движок TTS
engine = pyttsx3.init()
engine.setProperty('rate', TTS_RATE)  # скорость речи
engine.setProperty('volume', 1.0)     # громкость (0.0–1.0)

# def speak(text: str):
#     print(f"🗣 Jarvis говорит: {text}")
#     try:
#         engine.say(text)
#         engine.runAndWait()
#     except Exception as e:
#         print(f"❌ Ошибка синтеза речи: {e}")
