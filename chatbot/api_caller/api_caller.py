import json
import re
from enum import Enum
from pathlib import Path

import ollama

MODEL = "deepseek-r1:1.5b"


class ROLES(str, Enum):
    user = ("user",)
    system = "system"


class APICaller:
    def __init__(self):
        super().__init__()

    def get_response(self, content: str) -> ollama.ChatResponse:
        response = ollama.chat(model=MODEL, messages=content, think=False)
        return response

    def save_response(self, answer: str, question: str, log_file: Path) -> None:
        answer_cleaned = re.sub(r"<.*?>", "", answer).strip()
        print(f"Question: {question}")
        print("Response:")
        print(answer_cleaned)
        if log_file.exists():
            with log_file.open("r", encoding="utf-8") as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    messages = []
        else:
            messages = []

        messages.append({"role": ROLES.user, "content": question})
        messages.append({"role": ROLES.system, "content": answer_cleaned})

        with log_file.open("w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
