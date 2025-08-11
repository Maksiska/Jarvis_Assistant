import time
import threading
import speech_recognition as sr
from input.transcription import transcribe_audio

# Быстрые таймауты для реакции на stop_event
CHUNK_TIMEOUT = 0.5       # сек, шаг ожидания начала речи
CALIB_DURATION = 0.3      # быстрая калибровка шума

def _make_recognizer(pause_threshold: float, energy_threshold: float = 300) -> sr.Recognizer:
    r = sr.Recognizer()
    r.pause_threshold = pause_threshold
    r.energy_threshold = energy_threshold
    return r


def listen_full_phrase(
    wake_word: str = "джарвис",
    timeout: float = 8.0,
    pause_threshold: float = 1.2,
    stop_event: threading.Event | None = None,
    phrase_time_limit: float | None = None,
) -> str | None:
    """
    Слушает одну фразу, возвращает команду после ключевого слова.
    Возвращает:
      - строку команды (может быть пустой "" если не распознано),
      - "❌ Слово 'Jarvis' не услышал." если wake word не найден,
      - None при полном таймауте ожидания старта речи.

    Мгновенная отмена: если передан stop_event, проверяется каждые CHUNK_TIMEOUT сек
    во время ожидания начала речи. (Во время самой записи отмена произойдёт после
    завершения listen(), поэтому держите фразы короткими либо задайте phrase_time_limit.)
    """
    r = _make_recognizer(pause_threshold)

    with sr.Microphone() as source:
        print("🎤 Слушаю полную фразу...")
        try:
            r.adjust_for_ambient_noise(source, duration=CALIB_DURATION)
        except Exception:
            pass

        waited = 0.0
        audio = None

        # Ждём начала речи короткими тайм-слотами, чтобы быстро реагировать на stop
        while waited < timeout:
            if stop_event and stop_event.is_set():
                print("⏹ Остановлено до начала записи.")
                return ""

            try:
                # ждём появления речи не дольше CHUNK_TIMEOUT
                audio = r.listen(
                    source,
                    timeout=CHUNK_TIMEOUT,
                    phrase_time_limit=phrase_time_limit  # можно задать верхнюю границу длительности фразы
                )
                print("✅ Фраза записана.")
                break  # ушли записывать/распознавать
            except sr.WaitTimeoutError:
                waited += CHUNK_TIMEOUT
                continue
            except Exception as e:
                print(f"⚠️ Ошибка прослушивания: {e}")
                time.sleep(CHUNK_TIMEOUT)
                waited += CHUNK_TIMEOUT

        if audio is None:
            print("⌛ Время ожидания истекло.")
            return

    # Если уже после записи нажали стоп — считаем отменой
    if stop_event and stop_event.is_set():
        print("⏹ Остановлено после записи, до распознавания.")
        return

    # Распознаём
    text_raw = transcribe_audio(audio)
    if not text_raw:
        print("🤷 Ничего не распознано.")
        return

    text = text_raw.lower().strip()
    print(f"[DEBUG] Распознано: {text}")

    if wake_word and wake_word in text:
        command = text.split(wake_word, 1)[1].strip()
        print(f"📋 Команда: {command}")
        return command

    print("❌ Слово 'Jarvis' не услышал.")
    return


def lisen_nunder(   # оставляю исходное имя, только добавляю stop_event
    timeout: float = 8.0,
    pause_threshold: float = 1.2,
    stop_event: threading.Event | None = None,
    phrase_time_limit: float | None = None,
) -> str:
    """
    Слушает одну фразу без ключевого слова.
    Возвращает распознанный текст, либо сервисные строки как раньше.
    """
    r = _make_recognizer(pause_threshold)

    with sr.Microphone() as source:
        print("🎤 Слушаю выбор...")
        try:
            r.adjust_for_ambient_noise(source, duration=CALIB_DURATION)
        except Exception:
            pass

        waited = 0.0
        audio = None
        while waited < timeout:
            if stop_event and stop_event.is_set():
                print("⏹ Остановлено до начала записи (выбор).")
                return ""

            try:
                audio = r.listen(
                    source,
                    timeout=CHUNK_TIMEOUT,
                    phrase_time_limit=phrase_time_limit
                )
                print("✅ Фраза записана.")
                break
            except sr.WaitTimeoutError:
                waited += CHUNK_TIMEOUT
                continue
            except Exception as e:
                print(f"⚠️ Ошибка прослушивания: {e}")
                time.sleep(CHUNK_TIMEOUT)
                waited += CHUNK_TIMEOUT

        if audio is None:
            print("⌛ Время ожидания истекло.")
            return

    if stop_event and stop_event.is_set():
        print("⏹ Остановлено после записи (выбор).")
        return

    text_raw = transcribe_audio(audio)
    if not text_raw:
        print("🤷 Ничего не распознано.")
        return 

    text = text_raw.lower().strip()
    print(f"[DEBUG] Распознано: {text}")
    return text
