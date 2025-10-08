import logging
import sys


class LevelColorFormatter(logging.Formatter):
    """Formateador que colorea los niveles de logging"""

    LEVEL_COLORS = {
        "DEBUG": "\033[46m\033[97m",
        "INFO": "\033[44m\033[97m",
        "WARNING": "\033[43m\033[97m",
        "ERROR": "\033[41m\033[97m",
        "CRITICAL": "\033[45m\033[97m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelname, self.LEVEL_COLORS["INFO"])
        colored_level = f"{level_color}[{record.levelname}]{self.LEVEL_COLORS['RESET']}"
        record.msg = f"{colored_level} {record.msg}"
        return super().format(record)


def setup_logging():
    """Configurar TODOS los loggers de Uvicorn"""
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "uvicorn.server",
    ]

    for logger_name in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LevelColorFormatter("%(message)s"))
        logger.addHandler(handler)
        logger.propagate = False


def get_logger():
    """Obtener el logger configurado"""
    return logging.getLogger("uvicorn")
