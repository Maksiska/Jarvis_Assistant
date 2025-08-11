from core.command_router import route_command
from core.semantic_cleaner import semantic_clean_via_llm
from utils.helpers import clean_text, contains_exit_command
from utils.constants import EXIT_COMMANDS
from llm.emotion_classifier import classify_emotion
from output.text_output import print_response
# from output.speech_output import speak
from core.memory import add_message

def process_input(user_text: str) -> bool:
    cleaned = clean_text(user_text)

    if not cleaned or cleaned == None:
        print("🤷 Я не понял, что вы сказали.")
        return

    if contains_exit_command(cleaned, EXIT_COMMANDS):
        # speak("До встречи!")
        print("🚪 Завершаю работу.")
        return 

    emotion = classify_emotion(cleaned)
    print(f"🧠 Обнаружена эмоция: {emotion}")

    add_message(role="user", content=cleaned)

    semantic = semantic_clean_via_llm(cleaned)
    print(f"🧹 Очищено для поиска: {semantic}")

    response = route_command(semantic)

    add_message(role="bot", content=response)

    return response
