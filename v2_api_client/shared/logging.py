import logging
import sys

import environ
from django_log_formatter_ecs import ECSFormatter


def make_record_with_extra(
    self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None
):
    record = original_makeRecord(
        self, name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
    )
    record.extra_details = extra
    return record


original_makeRecord = logging.Logger.makeRecord
logging.Logger.makeRecord = make_record_with_extra


class AuditLogFormatter(ECSFormatter):
    def format(self, record):
        formatted_log = f"AUDIT LOG - {record.levelname} - {record.msg}"
        if extra_details := getattr(record, "extra_details", None):
            formatted_log += f" - {extra_details}"

        return formatted_log


root = environ.Path(__file__) - 4
env = environ.Env(
    DEBUG=(bool, False),
)

PRODUCTION_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "ecs_formatter": {
            "()": ECSFormatter,
        },
        "simple": {"format": "%(levelname)s %(message)s"},
        "audit_log": {"()": AuditLogFormatter},
    },
    "handlers": {
        "ecs": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "ecs_formatter",
        },
        "audit_log": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "audit_log",
        },
    },
    "root": {
        "handlers": [
            "ecs",
        ],
        "level": env("ROOT_LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "audit_trail": {
            "handlers": [
                "audit_log",
            ],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django": {
            "handlers": [
                "ecs",
            ],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.server": {
            "handlers": [
                "ecs",
            ],
            "level": env("DJANGO_SERVER_LOG_LEVEL", default="ERROR"),
            "propagate": False,
        },
        "django.request": {
            "handlers": [
                "ecs",
            ],
            "level": env("DJANGO_REQUEST_LOG_LEVEL", default="ERROR"),
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": [
                "ecs",
            ],
            "level": env("DJANGO_DB_LOG_LEVEL", default="ERROR"),
            "propagate": False,
        },
    },
}
audit_logger = logging.getLogger("audit_trail")
