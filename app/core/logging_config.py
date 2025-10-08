import logging
import sys


class LevelColorFormatter(logging.Formatter):
    LEVEL_BACKGROUNDS = {
        "DEBUG": "\033[45m",
        "INFO": "\033[44m",
        "WARNING": "\033[43m",
        "ERROR": "\033[41m",
        "CRITICAL": "\033[45m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        level_bg = self.LEVEL_BACKGROUNDS.get(
            record.levelname, self.LEVEL_BACKGROUNDS["INFO"]
        )

        if record.name == "app":
            app_text_colors = {
                "INFO": "\033[36m",
                "WARNING": "\033[93m",
                "ERROR": "\033[91m",
                "default": "\033[97m",
            }
            text_color = app_text_colors.get(
                record.levelname, app_text_colors["default"]
            )
        else:
            text_color = "\033[37m"

        colored_level = (
            f"{level_bg}\033[97m[{record.levelname}]{self.LEVEL_BACKGROUNDS['RESET']}"
        )
        record.msg = (
            f"{colored_level} {text_color}{record.msg}{self.LEVEL_BACKGROUNDS['RESET']}"
        )
        return super().format(record)


def setup_logging():
    loggers_to_configure = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "uvicorn.server",
        "watchfiles",
        "app",
    ]

    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LevelColorFormatter("%(message)s"))
        logger.addHandler(handler)
        logger.propagate = False


def get_logger():
    return logging.getLogger("app")
