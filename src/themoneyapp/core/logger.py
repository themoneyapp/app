"""logger for the themoneyapp project."""

import structlog


logger = structlog.get_logger()
bind_contextvars = structlog.contextvars.bind_contextvars
unbind_contextvars = structlog.contextvars.unbind_contextvars
