import sys
from importlib import resources
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLineEdit

from chatbot.api_caller.api_caller import APICaller

ui_path = resources.files(__package__) / "chat_dialog.ui"
FormClass, _ = uic.loadUiType(ui_path)


class ChatDialog(QDialog, FormClass):  # type: ignore
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.button_box: QDialogButtonBox
        self.content: QLineEdit
        self.response_field: QLineEdit

        self.api_caller = APICaller()

        self.button_box.accepted.connect(self.send_content)

    def send_content(self):
        question = self.content.text()
        file_path = Path(__file__).parent.parent / "api_caller" / "app.log"
        with open(file_path, "r") as f:
            logs = f.read()
        content = logs + f"Question: {question}"
        response = self.api_caller.get_response(content)
        answer = response["message"]["content"]
        self.api_caller.save_response(answer, question)
        self.response_field.setText(answer)


app = QApplication(sys.argv)
window = ChatDialog()
window.show()
app.exec()
