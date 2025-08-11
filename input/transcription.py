import speech_recognition as sr

recognizer = sr.Recognizer()

def transcribe_audio(audio):
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        return text
    except sr.UnknownValueError:
        print("🤷 Я не понял, что вы сказали.")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Ошибка при подключении к сервису распознавания речи: {e}")
        return None
