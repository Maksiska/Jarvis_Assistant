from llm.ollama_client import ask_llm
from utils.helpers import extract_json_from_text

EXAMPLES = """
Вход: "открой блокнот" или "открой калькулятор"
Ответ: {"action_type": "console", "action_target": "", "console_command": "notepad"} или {"action_type": "console", "action_target": "", "console_command": "calc"}

Вход: "открой браузер"
Ответ: {"action_type": "console", "action_target": "browser", "console_command": "start chrome"}

Вход: "открой сайт ютуб"
Ответ: {"action_type": "open_url", "action_target": "https://youtube.com", "console_command": "start https://youtube.com"}

Вход: "открой файл новый текстовый документ"
Ответ: {"action_type": "search_files", "action_target": "новый текстовый документ", "console_command": ""}

Вход: "открой папку AI"
Ответ: {"action_type": "open_folder", "action_target": "AI", "console_command": ""}

Вход: "выключи компьютер"
Ответ: {"action_type": "console", "action_target": "", "console_command": "shutdown /s /t 3"}

Вход: "прочитай анекдот"
Ответ: {"action_type": "unknown", "action_target": "", "console_command": ""}

Вход: "открой приложение telegram"
Ответ: {"action_type": "launch_app", "action_target": "telegram", "console_command": ""}

Вход: "запусти CapCut"
Ответ: {"action_type": "launch_app", "action_target": "CapCut", "console_command": ""}

"""

def interpret_action(user_text: str) -> dict:
    prompt = f"""
Ты — интеллектуальный интерпретатор команд пользователя, от тебя зависит работа голового помощника.
Твоя основная задача просто исходя из запроса составить JSON по примеру и все, в зависимости от него будут выполняться различные действия.

Для команды пользователя верни результат в формате JSON:

{{
  "action_type": "...",
  "action_target": "...",
  "console_command": "..."
}}

Обязательно ставь фигурные скобки, чтобы код мог прочитать твой ответ.
Сама структура JSON файла должна быть в твоем ответе обязательно.

Где:
- action_type — тип действия (например: "launch_app", "open_folder", "open_url", "console", "unknown", "search_files")
- action_target — цель (например: "browser", "Downloads", "https://youtube.com")
- console_command — фактическая консольная команда, которая будет выполнена (например: "start chrome", "start AI", "shutdown /s /t 3")

Примеры:

{EXAMPLES}

Теперь обработай и верни строго формат JSON и в нем обязательно укажи action_type:

"{user_text}"

Ответ:
"""

    raw_response = ask_llm(prompt)
    print(f"[DEBUG] Ответ LLM:\n{raw_response}")

    parsed = extract_json_from_text(raw_response)
    if parsed and "action_type" in parsed and "action_target" in parsed and "console_command" in parsed:
        return parsed
    print("⚠️ Некорректный JSON от LLM!")
    return {"action_type": "unknown", "action_target": "", "console_command": ""}