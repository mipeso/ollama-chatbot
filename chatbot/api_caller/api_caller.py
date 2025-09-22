import json
import logging
import re
from pathlib import Path

import ollama

MODEL = "deepseek-r1:1.5b"
ROLE = "user"


logging.getLogger("httpx").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class APICaller:
    def __init__(self):
        super().__init__()

    def create_message_json(self, content: str) -> dict:
        return {
            "role": ROLE,
            "content": content,
        }

    def get_response(self, content: str) -> ollama.ChatResponse:
        message = self.create_message_json(content)
        response = ollama.chat(
            model=MODEL,
            messages=[message],
        )
        return response

    def save_response(self, answer: str, question: str, log_file: Path) -> None:
        print(log_file)
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        LOGGER.addHandler(handler)
        try:
            answer_cleaned = re.sub(r"<.*?>", "", answer).strip()
            print(f"Question: {question}")
            print("Response:")
            print(answer_cleaned)
            entry = {"Q": question, "A": answer_cleaned}
            LOGGER.info(json.dumps(entry, ensure_ascii=False))
        finally:
            LOGGER.removeHandler(handler)
            handler.close()
