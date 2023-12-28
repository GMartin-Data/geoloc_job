import logging

from rich.logging import RichHandler


def setup_logging():
    # File handler configuration
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.WARNING)
    file_format = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_format)

    # Basic configuration
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(), file_handler],
    )
