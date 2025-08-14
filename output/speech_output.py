# output/speech_output.py
import os
import pyttsx3
from dotenv import load_dotenv

load_dotenv()

TTS_RATE = int(os.getenv("TTS_VOICE_RATE", os.getenv("TTS_RATE", 175)))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))
TTS_VOICE_NAME = os.getenv("TTS_VOICE_NAME", "")

def _configure_engine(engine: pyttsx3.Engine):
    engine.setProperty("rate", TTS_RATE)
    engine.setProperty("volume", TTS_VOLUME)
    if TTS_VOICE_NAME:
        try:
            voices = engine.getProperty("voices") or []
            for v in voices:
                if TTS_VOICE_NAME.lower() in (v.name or "").lower():
                    engine.setProperty("voice", v.id)
                    break
        except Exception:
            pass

def speak(text: str):
    """
    Синхронно произнести text. Создаёт НОВЫЙ движок на каждый вызов,
    чтобы избежать зависаний после первого прогона.
    """
    if not text:
        return
    try:
        engine = pyttsx3.init()  # отдельный движок на вызов
        _configure_engine(engine)
        engine.say(str(text))
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"❌ Ошибка синтеза речи: {e}")
