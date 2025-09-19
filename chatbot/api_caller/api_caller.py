import logging
import os
import re

import ollama

MODEL = "deepseek-r1:1.5b"
ROLE = "user"

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "app.log"),
    encoding="utf-8",
    level=logging.INFO,
    format="%(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


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

    def save_response(self, answer: str, question: str) -> None:
        print(f"Question: {question}")
        print("Response:")
        print(answer)
        answer_cleaned = re.sub(r"<.*?>", "", answer).strip()
        LOGGER.info(f"Question: {question}")
        LOGGER.info(f"Answer: {answer_cleaned}")
