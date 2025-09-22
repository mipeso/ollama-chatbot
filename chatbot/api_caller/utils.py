from pathlib import Path

path = Path(__file__).parent / "logs"


def init_log(name: str, extension: str = "log") -> None:
    Path(path / f"{name}.{extension}").touch()


def delete_log(name: str, extension: str = "log") -> None:
    print(Path(path / f"{name}.{extension}"))
    Path(path / f"{name}.{extension}").unlink(missing_ok=True)


def get_logs() -> list[Path]:
    logs = []
    for file in path.glob("*.log"):
        logs.append(file)
    return logs
