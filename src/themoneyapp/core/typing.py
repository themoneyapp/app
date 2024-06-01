"""Commonly used types.

import themoneyapp.core.typing as mt

mt.Callable[..., mt.Awaitable[str]]
"""

from collections.abc import Awaitable, Callable, Coroutine


__all__ = ("Awaitable", "Callable", "Coroutine")
