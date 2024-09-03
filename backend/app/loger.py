import logging
import os
import app.config


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s:%(name)s:%(process)d:%(lineno)d %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "logfile": {
            "formatter": "default",
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": app.config.LOG_FILE_NAME,
            "backupCount": 2,
        },
        "consol": {
            "formatter": "default",
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "log": {
            "level": "INFO",
            "handlers": [
                "logfile",
            ],
        },
    },
    "root": {"level": "INFO", "handlers": ["logfile", "consol"]},
}


def create_log_folder(folder=app.config.LOG_DIR):
    if not os.path.exists(folder):
        os.mkdir(folder)
