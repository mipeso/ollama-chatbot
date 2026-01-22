import json
import re
from enum import Enum
from pathlib import Path

import ollama
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QInputDialog,
    QLabel,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from chatbot.core.chat_manager import ROLES, ChatManager
from chatbot.core.utils import delete_log, get_logs, init_log


class MessageType(str, Enum):
    QUESTION = "question"
    ANSWER = "answer"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("chatbot/gui/main_window.ui", self)

        self.chat_list = self.ui.chat_list
        self.scroll_area = self.ui.scroll_area
        self.add_button = self.ui.add_button
        self.delete_button = self.ui.delete_button
        self.vertical_layout = self.ui.verticalLayout
        self.text_box = self.ui.text_box
        self.send_button = self.ui.send_button
        self.model_combobox = self.ui.model_combobox

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.chat_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # List for holding inputs to model
        self.data = []

        # Populate model combobox
        self.populate_model_list()
        self.init_model()
        self.model_combobox.currentTextChanged.connect(self.init_model)

        self.add_button.clicked.connect(self.add_chat)
        self.delete_button.clicked.connect(self.delete_chat)
        self.chat_list.currentItemChanged.connect(self.load_chat)
        self.send_button.clicked.connect(self.send_content)

    def populate_model_list(self) -> None:
        models = ollama.list()
        for model in models["models"]:
            self.model_combobox.addItem(model["model"])
        self.api_caller = ChatManager(self.model_combobox.currentText())

    def init_model(self) -> None:
        self.api_caller = ChatManager(self.model_combobox.currentText())
        self.chat_list.clear()
        logs = get_logs(self.model_combobox.currentText())
        if logs:
            for log in logs:
                self.chat_list.addItem(log.stem)

    def add_chat(self) -> None:
        text, ok = QInputDialog.getText(None, "New Chat", "Enter chat name:")
        if ok and text:
            self.chat_list.addItem(text)
            init_log(text, self.model_combobox.currentText())
            new_item = self.chat_list.item(self.chat_list.count() - 1)
            self.chat_list.setCurrentItem(new_item)

    def delete_chat(self) -> None:
        for item in self.chat_list.selectedItems():
            row = self.chat_list.row(item)
            self.chat_list.takeItem(row)
            delete_log(item.text(), self.model_combobox.currentText())

    def clear_layout(self, layout: QVBoxLayout) -> None:
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
            / self.model_combobox.currentText()
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
            / self.model_combobox.currentText()
            / f"{self.chat_list.currentItem().text()}.log"
        )

        messages = list(self.data)
        messages.append({"role": ROLES.user, "content": question})

        response = self.api_caller.get_response(messages)
        answer = response["message"]["content"]
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
                "color: black; background-color: lightblue; border-radius: 10px; padding: 2px; margin: 4px;"
            )
        elif message_type == MessageType.ANSWER:
            msg_label.setStyleSheet(
                "color: black; background-color: lightgreen; border-radius: 10px; padding: 2px; margin: 4px;"
            )
        self.scroll_layout.addWidget(msg_label)
        self.text_box.clear()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
