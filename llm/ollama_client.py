import ollama
import os

def ask_llm(prompt: str) -> str:
    try:
        model = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        return response.get("message", {}).get("content", "").strip() or "⚠️ Модель не вернула ответа."
    
    except Exception as e:
        return f"⚠️ Ошибка при вызове LLM: {e}"
