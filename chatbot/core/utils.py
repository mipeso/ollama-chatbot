from pathlib import Path

log_folder = Path(__file__).parent.parent / "logs"


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
