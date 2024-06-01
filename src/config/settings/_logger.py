"""Utils to configure structlog and load stdlib logging configuration."""

from __future__ import annotations

import logging
import logging.config
import logging.handlers
import typing as t
from pathlib import Path

import structlog
from structlog.typing import EventDict, WrappedLogger

from themoneyapp.core import jsonlib


__all__ = (
    "get_logging_config",
    "get_third_party_logging_config",
)


# Typing


ProcessorType = t.Callable[[WrappedLogger | logging.Logger, str, EventDict], EventDict]


# Filters


class StdErrFilter(logging.Filter):
    """ilter for the stderr stream.

    Doesn't print records below ERROR to stderr to avoid dupes.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return not record.levelno < logging.ERROR


class StdOutFilter(logging.Filter):
    """Filter for the stdout stream.

    Doesn't print records above WARNING to stdout to avoid dupes.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


# Processors


def check_message_field(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    """
    Check if ``message`` field is present in the *event_dict*.

    If present and its value is same as the ``event`` field,
    remove the ``message`` field. Otherwise, raise an error.
    """
    if "message" in event_dict:
        message_value = str(event_dict.get("message", ""))
        event_value = event_dict.get("event", "")
        if message_value.strip() == event_value.strip():
            event_dict.pop("message")

        else:
            msg = "Avoid using 'message' field"
            raise ValueError(msg)

    return event_dict


def remove_processors_meta_safe(
    _: WrappedLogger, __: str, event_dict: EventDict
) -> EventDict:
    """
    Remove ``_record`` and ``_from_structlog`` from *event_dict*.

    These keys are added to the event dictionary, before
    `ProcessorFormatter`'s *processors* are run.
    """
    event_dict.setdefault("_record", None)
    event_dict.setdefault("_from_structlog", None)
    structlog.stdlib.ProcessorFormatter.remove_processors_meta(_, __, event_dict)

    return event_dict


# Configure all logs to be handled by structlog `ProcessorFormatter` and
# rendered either as pretty colored console lines or as single JSON
# lines with structured tracebacks
def get_logging_config(
    filename: str, loglevel: int, *, json_logs: bool = False, colors: bool = True
) -> dict[str, t.Any]:
    """Configure python stdlib's logging.

    https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging

    """
    filename_path = Path(filename).resolve()
    if filename_path.is_dir() is True:
        msg = f'filename "{filename}" must be a file'
        raise ValueError(msg)

    filename_path.parent.mkdir(parents=True, exist_ok=True)

    root_log_level_name = logging.getLevelName(loglevel)

    # To enable standard library logs to be formatted via structlog, we add this
    # `foreign_pre_chain` to both formatters.
    _foreign_pre_chain: list[ProcessorType] = [
        # Set the contextvars processor to be used for configuring structlog
        structlog.contextvars.merge_contextvars,
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Perform %-style formatting.
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Add a timestamp in ISO 8601 format.
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        # Add extra attributes of LogRecord objects to the event dictionary
        # so that values passed in the extra parameter of log methods pass
        # through to log output.
        structlog.stdlib.ExtraAdder(),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # raise an error whenever "message" field is used (when message != event values)
        check_message_field,
        # replace "event" key with "message" field
        structlog.processors.EventRenamer(to="event", replace_by="message"),
        # If some value is in bytes, decode it to a Unicode str.
        structlog.processors.UnicodeDecoder(),
        # Add callsite parameters.
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]

    base_formatter = "json" if json_logs else "plain"
    std_formatter = base_formatter
    if std_formatter == "plain" and colors is True:
        std_formatter = "colored"

    std_logger_config: dict[str, t.Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": [
                    *_foreign_pre_chain,
                    # If the "exc_info" key in the event dict is either true or a
                    # sys.exc_info() tuple, remove "exc_info" and render the exception
                    # with traceback into the "exception" key.
                    # NOTE: adding it separately as ConsoleRenderer complains about
                    # `format_exc_info` being in the chain.
                    structlog.processors.format_exc_info,
                ],
                # These run on ALL entries after the pre_chain is done.
                "processors": [
                    remove_processors_meta_safe,
                    structlog.processors.JSONRenderer(serializer=jsonlib.dumps),
                ],
            },
            "plain": {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": _foreign_pre_chain,
                # These run on ALL entries after the pre_chain is done.
                "processors": [
                    remove_processors_meta_safe,
                    structlog.dev.ConsoleRenderer(
                        colors=False, exception_formatter=structlog.dev.plain_traceback
                    ),
                ],
            },
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": _foreign_pre_chain,
                # These run on ALL entries after the pre_chain is done.
                "processors": [
                    remove_processors_meta_safe,
                    structlog.dev.ConsoleRenderer(
                        colors=True, exception_formatter=structlog.dev.rich_traceback
                    ),
                ],
            },
        },
        "filters": {
            "stderr_filter": {
                "()": StdErrFilter,
            },
            "stdout_filter": {
                "()": StdOutFilter,
            },
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": root_log_level_name,
                "formatter": std_formatter,
                "filters": ["stdout_filter"],
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": std_formatter,
                "filters": ["stderr_filter"],
                "stream": "ext://sys.stderr",
            },
            "filehandler": {
                "class": "logging.handlers.WatchedFileHandler",
                "level": root_log_level_name,
                "formatter": base_formatter,
                "filename": str(filename_path),
            },
            "mail_admins": {
                "class": "django.utils.log.AdminEmailHandler",
                "level": "ERROR",
                "include_html": True,
            },
        },
        "loggers": {},
        "root": {
            "level": root_log_level_name,
            "handlers": ["stdout", "stderr", "filehandler", "mail_admins"],
        },
    }

    handler_names = std_logger_config["root"]["handlers"]

    for logger_name, config in get_third_party_logging_config(
        root_log_level_name
    ).items():
        std_logger_config["loggers"][logger_name] = {
            "handlers": handler_names,
            "level": config["level"],
            "propagate": config.get("propagate", False),
        }

    structlog.configure_once(
        processors=[
            # If log level is too low, abort pipeline and throw away log entry.
            structlog.stdlib.filter_by_level,
            *_foreign_pre_chain,
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.make_filtering_bound_logger(min_level=loglevel),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return std_logger_config


def get_third_party_logging_config(loglevel: str) -> dict[str, dict[str, t.Any]]:
    return {
        "": {"level": loglevel, "propagate": False},
        "celery": {"level": loglevel, "propagate": False},
        "django": {"level": "WARNING", "propagate": False},
        "django.request": {"level": "ERROR", "propagate": False},
        "django.security.DisallowedHost": {"level": "ERROR", "propagate": True},
        "django.security": {"level": "WARNING", "propagate": False},
        "psycopg": {"level": "DEBUG", "propagate": False},
        "requests": {"level": "WARNING", "propagate": False},
        "kombu": {"level": "WARNING", "propagate": False},
        "urllib3": {"level": "WARNING", "propagate": False},
        "asyncio": {"level": "WARNING", "propagate": False},
        "redis": {"level": "WARNING", "propagate": False},
        "uvicorn": {"level": "WARNING", "propagate": False},
        "gunicorn": {"level": "INFO", "propagate": False},
        "uvicorn.access": {"level": "INFO", "propagate": False},
        "gunicorn.access": {"level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "ERROR", "propagate": False},
        "gunicorn.error": {"level": "ERROR", "propagate": False},
        "watchdog": {"level": "ERROR", "propagate": False},
        # Add other loggers as needed
    }
