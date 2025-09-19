from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
import os
import sys
from api_caller.api_caller import APICaller


class ChatDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.api_caller = APICaller()

        self.label = QLabel("What do you wish to know?")
        self.content = QLineEdit()
        self.ok_button = QPushButton("OK")
        self.response_field = QLineEdit()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.content)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.response_field)
        self.setLayout(layout)

        self.ok_button.clicked.connect(self.send_content)

    def send_content(self):
        question = self.content.text()
        file_path = os.path.join(os.getcwd(), "api_caller", "app.log")
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
