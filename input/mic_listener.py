import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_from_mic(timeout=5, phrase_time_limit=None):
    recognizer.pause_threshold = 1.6  # Увеличь, если пользователь делает паузы
    recognizer.energy_threshold = 300  # Настройка чувствительности (или отключи calibrate)

    try:
        with sr.Microphone() as source:
            print("🎤 Говорите (я слушаю)...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("✅ Получена аудиозапись.")
            return audio
    except sr.WaitTimeoutError:
        print("⌛ Никто не заговорил. Таймаут.")
        return None
    except Exception as e:
        print(f"❌ Ошибка микрофона: {e}")
        return None
