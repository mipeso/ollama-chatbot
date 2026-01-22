import json
import re
from enum import Enum
from pathlib import Path

import nltk
import ollama
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
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
from chatbot.core.embeddings_manager import EmbeddingsManager
from chatbot.core.utils import delete_log, get_logs, init_log

nltk.download("punkt_tab")


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
        self.text_input_field = self.ui.text_input_field
        self.send_button = self.ui.send_button
        self.model_combobox = self.ui.model_combobox
        self.model_combobox.setToolTip(
            "Choose a model that is capapble of chat.\nEmbedding models will not work."
        )
        self.input_file_field = self.ui.input_file_field
        self.browse_button = self.ui.browse_button
        self.input_file_field.setPlaceholderText("Provide a text file for reference...")

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.chat_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.embeddings_manager = EmbeddingsManager()
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
        self.browse_button.clicked.connect(self.browse)

    def populate_model_list(self) -> None:
        models = ollama.list()
        for model in models["models"]:
            self.model_combobox.addItem(model["model"])
        self.chat_manager = ChatManager(self.model_combobox.currentText())

    def init_model(self) -> None:
        self.chat_manager = ChatManager(self.model_combobox.currentText())
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

        question = self.text_input_field.text()
        self.add_message(question, MessageType.QUESTION)
        file_path = (
            Path(__file__).parent.parent
            / "logs"
            / self.model_combobox.currentText()
            / f"{self.chat_list.currentItem().text()}.log"
        )

        rag_context = None
        if self.input_file_field.text():
            # Read the file and embed its content
            rag_data = self.read_file(self.input_file_field.text())
            self.embeddings_manager.embed(rag_data)
            # Retrieve the most relevant text for the question
            retrieved_text = self.embeddings_manager.retrieve(question)
            # Combine retrieved text and user input
            rag_context = "\n".join(retrieved_text)

        messages = list(self.data)

        if rag_context:
            messages.append(
                {
                    "role": ROLES.user,
                    "content": f"Use this document as a reference:\n{rag_context}\n\nQuestion: {question}",
                }
            )
        else:
            messages.append({"role": ROLES.user, "content": question})

        # Get response from chat model
        response = self.chat_manager.get_response(messages)
        answer = response["message"]["content"]
        answer_cleaned = re.sub(r"<.*?>", "", answer).strip()

        # Save messages to log
        self.data.append({"role": ROLES.user, "content": question})
        self.data.append({"role": ROLES.system, "content": answer_cleaned})
        self.chat_manager.save_response(answer_cleaned, question, file_path)
        self.add_message(answer_cleaned, MessageType.ANSWER)
        self.input_file_field.setText("")

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
        self.text_input_field.clear()
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def browse(self):
        dialog = QFileDialog(self)
        file_path, _ = dialog.getOpenFileName(
            self, self.tr("Select File"), filter=self.tr("Text files (*.txt)")
        )
        self.input_file_field.setText(file_path)

    def read_file(self, file_path: str) -> list[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
        except FileNotFoundError:
            QMessageBox.critical(self, "", f"File {file_path} was not found.")
            return []

        sentences = nltk.sent_tokenize(text)

        return sentences
