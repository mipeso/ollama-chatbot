import json
import re
import sys
from enum import Enum
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from chatbot.api_caller.api_caller import ROLES, APICaller
from chatbot.api_caller.utils import delete_log, get_logs, init_log

ui_path = Path(__file__).parent / "main_window.ui"
FormClass, _ = uic.loadUiType(ui_path)


class MessageType(str, Enum):
    QUESTION = "question"
    ANSWER = "answer"


class MainWindow(QMainWindow, FormClass):  # type: ignore
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.chat_list: QListWidget
        self.scroll_area: QScrollArea
        self.add_button: QPushButton
        self.delete_button: QPushButton
        self.vertical_layout: QVBoxLayout
        self.text_box: QLineEdit
        self.send_button: QPushButton

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.api_caller = APICaller()
        self.data = []

        self.chat_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Fetch old chats
        logs = get_logs()
        if logs:
            for log in logs:
                self.chat_list.addItem(log.stem)

        self.add_button.clicked.connect(self.add_chat)
        self.delete_button.clicked.connect(self.delete_chat)
        self.chat_list.currentItemChanged.connect(self.load_chat)
        self.send_button.clicked.connect(self.send_content)

    def add_chat(self) -> None:
        text, ok = QInputDialog.getText(None, "New Chat", "Enter chat name:")
        if ok and text:
            self.chat_list.addItem(text)
            init_log(text)
            new_item = self.chat_list.item(self.chat_list.count() - 1)
            self.chat_list.setCurrentItem(new_item)

    def delete_chat(self) -> None:
        for item in self.chat_list.selectedItems():
            row = self.chat_list.row(item)
            self.chat_list.takeItem(row)
            delete_log(item.text())

    def clear_layout(self, layout: QVBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def load_chat(self, current_item: QListWidgetItem) -> None:
        self.data.clear()
        if not current_item:
            self.clear_layout(self.scroll_layout)
            return

        path = (
            Path(__file__).parent.parent
            / "api_caller"
            / "logs"
            / f"{current_item.text()}.log"
        )
        self.clear_layout(self.scroll_layout)
        with open(path, "r", encoding="utf-8") as file:
            try:
                messages = json.load(file)
            except json.JSONDecodeError:
                messages = []
        self.data.extend(messages)
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == ROLES.user:
                self.add_message(content, MessageType.QUESTION)
            elif role == ROLES.system:
                self.add_message(content, MessageType.ANSWER)

    def send_content(self):
        if not self.chat_list.currentItem():
            QMessageBox.warning(self, "", "Select a chat before sending a message.")
            return

        question = self.text_box.text()
        self.add_message(question, MessageType.QUESTION)
        file_path = (
            Path(__file__).parent.parent
            / "api_caller"
            / "logs"
            / f"{self.chat_list.currentItem().text()}.log"
        )

        messages = list(self.data)
        messages.append({"role": ROLES.user, "content": question})

        response = self.api_caller.get_response(messages)
        answer = response["message"]["content"]
        print(answer)
        answer_cleaned = re.sub(r"<.*?>", "", answer).strip()

        self.data.append({"role": ROLES.user, "content": question})
        self.data.append({"role": ROLES.system, "content": answer_cleaned})
        self.api_caller.save_response(answer_cleaned, question, file_path)
        self.add_message(answer_cleaned, MessageType.ANSWER)

    def add_message(self, message: str, message_type: MessageType) -> None:
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        msg_label.adjustSize()

        if message_type == MessageType.QUESTION:
            msg_label.setStyleSheet(
                "background-color: lightblue; border-radius: 10px; padding: 2px; margin: 4px;"
            )
        elif message_type == MessageType.ANSWER:
            msg_label.setStyleSheet(
                "background-color: lightgreen; border-radius: 10px; padding: 2px; margin: 4px;"
            )
        self.scroll_layout.addWidget(msg_label)
        self.text_box.clear()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
