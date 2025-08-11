import re
import json

def clean_text(text) -> str:
    if not isinstance(text, str):
        print(f"❌ Неверный тип: {type(text)} — {text!r}")
        return None
    return re.sub(r'\s+', ' ', text.strip())


def contains_exit_command(text: str, exit_commands: list) -> bool:
    lowered = text.lower()
    return any(cmd in lowered for cmd in exit_commands)

def extract_keywords(text: str, keywords: list) -> list:
    return [kw for kw in keywords if kw in text.lower()]

def debug_log(msg: str):
    print(f"[DEBUG] {msg}")

def normalize_text_for_vector(text: str) -> str:
    text = clean_text(text)
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

def extract_json_from_text(text: str):
    """Return a JSON object parsed from a text that may contain extra text."""
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and start < end:
        json_str = text[start:end + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None