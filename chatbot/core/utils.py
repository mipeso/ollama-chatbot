from pathlib import Path

import nltk
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

log_folder = Path(__file__).parent.parent / "logs"
nltk.download("punkt_tab")


def init_log(name: str, model: str, extension: str = "log") -> None:
    model_dir = Path(log_folder, model)
    if not model_dir.exists():
        model_dir.mkdir(parents=True, exist_ok=True)
    Path(model_dir / f"{name}.{extension}").touch()


def delete_log(name: str, model: str, extension: str = "log") -> None:
    model_dir = Path(log_folder / model)
    Path(model_dir / f"{name}.{extension}").unlink(missing_ok=True)
    if not any(model_dir.iterdir()):
        model_dir.rmdir()


def get_logs(model: str) -> list[Path]:
    file_path = log_folder / model
    logs = []
    for file in file_path.glob("*.log"):
        logs.append(file)
    return logs


def read_file(main_window: QMainWindow, file_path: str) -> list[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except FileNotFoundError:
        QMessageBox.critical(main_window, "", f"File {file_path} was not found.")
        return []

    sentences = nltk.sent_tokenize(text)

    return sentences


def browse_files(main_window: QMainWindow):
    dialog = QFileDialog(main_window)
    file_path, _ = dialog.getOpenFileName(
        main_window,
        main_window.tr("Select File"),
        filter=main_window.tr("Text files (*.txt)"),
    )
    main_window.input_file_field.setText(file_path)
