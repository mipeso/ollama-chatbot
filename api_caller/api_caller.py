import ollama

MODEL = "deepseek-r1:7b"
ROLE = "user"


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
