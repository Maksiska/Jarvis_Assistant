# 🤖 Jarvis Assistant

Локальный голосовой и текстовый ассистент, который понимает команды с помощью LLM, выполняет действия на компьютере и **кэширует команды в SQLite** для мгновенного повторного запуска без обращения к модели.

---

## 📖 Описание

Jarvis Assistant:
- Принимает команды **голосом**.
- Преобразует их в **структурированные действия** через LLM (Ollama).
- Выполняет действия: запуск приложений, открытие URL, поиск/открытие файлов и папок, консольные команды.
- **Запоминает** команды в SQLite и при повторе выполняет их **без LLM**.

---

## 🚀 Основные возможности

- 🎤 Голосовое управление (wake word: «джарвис»).
- 🧠 Интерпретация команд в JSON (LLM через Ollama).
- ⚙️ Действия ОС: `launch_app`, `open_url`, `search_files`, `open_folder`, `console`.
- 💾 **SQLite‑кэш**: сохранение `query`, `action_type`, `action_target`, `console_command`.
- 😃 Простейшая классификация эмоций.
- 💬 GUI на PyQt6 (чат).
- 🖥 Оффлайн: вся логика и БД локальные.

---

## 🗂 Структура проекта
```
Jarvis_Assistant/
├── core/
│ ├── actions.py
│ ├── agent.py
│ ├── command_router.py
│ ├── db.py 
│ ├── memory.py
│ ├── semantic_cleaner.py
│
├── input/
│ ├── vad.py
│ ├── transcription.py
│ ├── mic_listener.py
│
├── llm/
│ ├── ollama_client.py
│ ├── action_interpreter.py
│ ├── emotion_classifier.py
│
├── utils/
│ ├── constants.py
│ ├── helpers.py
│
├── output/
│ ├── text_output.py
│ ├── speech_output.py
│
├── main.py
├── .env
```
---

## 📦 Установка
```
git clone https://github.com/*yourname*/Jarvis_Assistant.git
cd Jarvis_Assistant
python -m venv .venv
.\.venv\Scripts\activate 
pip install -r requirements.txt

# В релизах скачайте архив Ollama.rar и распакуйте его в корневую папку проекта
```

