# core/command_router.py
from core.actions import execute_action, BD_actions
from llm.action_interpreter import interpret_action
from core import db as db

# Инициализируем БД при импорте модуля
db.init_db()

# Ответы, которые трактуем как неуспех выполнения
_BAD_RESULTS = {
    "", "Ошибка при выполнении действия.", "Выбор отменён.",
    "Я вас не понял", None, "Ничего не найдено.", "Приложение не найдено",
    "Команда не распознана", "Неизвестный тип действия."
}

def _is_success(result: str) -> bool:
    return result not in _BAD_RESULTS

def route_command(command_text: str) -> str:
    if not command_text:
        return "Команда не распознана"

    print(f"📥 Получена команда: {command_text}")

    # 1) Пытаемся найти точное совпадение запроса в БД
    cached = db.get_action_by_query(command_text)
    if cached:
        print("🗂 Найдено в БД — выполняю без LLM.")
        # Выполняем сразу через BD_actions (использует сохранённые поля)
        BD_actions(
            cached["action_type"],
            cached["action_target"],
            cached["console_command"]
        )
        return "Выполняю"

    # 2) Если в БД нет — обращаемся к LLM за разбором
    print("📡 Запрашиваем у LLM интерпретацию...")
    action = interpret_action(command_text)

    # 3) Выполняем действие и получаем «факт» выполнения (путь/URL/команда)
    executed_value = execute_action(
        action["action_type"],
        action["action_target"],
        action["console_command"]
    )
    action["action_target"] = executed_value  # фиксируем, что реально было запущено/открыто

    # 4) Если выполнение валидное — сохраняем в БД
    if action["action_type"] in ["launch_app", "open_url", "search_files", "open_folder", "console"] and _is_success(action["action_target"]):
        # В БД пишем: query, action_type, action_target(факт), console_command(из LLM)
        db.save_action(
            query=command_text,
            action_type=action["action_type"],
            action_target=action["action_target"],
            console_command=action.get("console_command", "")
        )
        print("✅ Сохранено в БД.")

        return "Выполняю"

    # 5) Некорректное действие
    return "Непонятное действие"
