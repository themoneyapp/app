"""Utils to handle JSON type data."""

from __future__ import annotations

import datetime
import json
import typing as t
from collections import deque
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from re import Pattern
from types import GeneratorType
from uuid import UUID

import canonicaljson
import pydantic as pyd

import themoneyapp.core.typing as mt
from themoneyapp.core.datetime import isoformat


def decimal_encoder(dec_value: Decimal) -> int | float:
    """Encodes a Decimal as int of there's no exponent, otherwise float.

    This is useful when we use ConstrainedDecimal to represent Numeric(x,0)
    where a integer (but not int typed) is used. Encoding this as a float
    results in failed round-tripping between encode and parse.
    Our Id type is a prime example of this.

    >>> decimal_encoder(Decimal("1.0"))
    1.0

    >>> decimal_encoder(Decimal("1"))
    1
    """
    if int(dec_value.as_tuple().exponent) >= 0:
        return int(dec_value)

    return float(dec_value)


ENCODERS_BY_TYPE: dict[type[t.Any], mt.Callable[[t.Any], t.Any]] = {
    bytes: lambda o: o.decode(),
    datetime.date: isoformat,
    datetime.datetime: isoformat,
    datetime.time: isoformat,
    datetime.timedelta: lambda td: td.total_seconds(),
    Decimal: decimal_encoder,
    Enum: lambda o: o.value,
    frozenset: list,
    deque: list,
    GeneratorType: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    Path: str,
    Pattern: lambda o: o.pattern,
    set: list,
    UUID: str,
}


def _json_fallback_handler(obj: object) -> t.Any:  # noqa: ANN401
    """Serialize custom datatypes and pass the rest to __structlog__ & repr()."""
    if hasattr(obj, "__structlog__"):
        return obj.__structlog__()

    return repr(obj)


def _pydantic_encoder(obj: object) -> t.Any:  # noqa: ANN401
    """Try to serialize the dataclass and pyd.BaseModel objects."""
    if isinstance(obj, pyd.BaseModel):
        return obj.model_dump(mode="json")

    if is_dataclass(obj):
        return asdict(obj)  # type: ignore[arg-type]

    # Check the class type and its superclasses for a matching encoder
    for base in obj.__class__.__mro__[:-1]:
        try:
            encoder = ENCODERS_BY_TYPE[base]

        except KeyError:
            continue

        return encoder(obj)

    # We have exited the for loop without finding a suitable encoder
    msg = f"Object of type '{obj.__class__.__name__}' is not JSON serializable"
    raise TypeError(msg)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder for various types of objects."""

    def default(self, obj: object) -> t.Any:  # noqa: ANN401
        """Return a serializable object for `obj`."""
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)

        if isinstance(obj, (set, tuple)):
            return list(obj)

        if isinstance(obj, memoryview):
            return str(obj)

        encoders = [
            _pydantic_encoder,
            _json_fallback_handler,
            canonicaljson.encode_canonical_json,
        ]

        for f in encoders:
            try:
                return f(obj)

            except TypeError:  # noqa: PERF203
                pass

        return super().default(obj)


def dumps(  # noqa: PLR0913
    obj: object,
    *,
    ensure_ascii: bool = False,
    allow_nan: bool = False,
    separators: tuple[str, ...] = (",", ":"),
    sort_keys: bool = True,
    default: mt.Callable[[object], t.Any] | None = None,  # skip this  # noqa: ARG001
    **kwargs: t.Any,  # noqa: ANN401
) -> str:
    """Serialize `obj` to a JSON formatted `str`."""
    _canonical_encoder = JSONEncoder(
        ensure_ascii=ensure_ascii,
        allow_nan=allow_nan,
        separators=separators,  # type: ignore[arg-type]
        sort_keys=sort_keys,
        **kwargs,
    )

    s = _canonical_encoder.encode(obj)
    return s.encode("utf-8").decode("utf-8")


def loads(obj: t.AnyStr, **kwargs: t.Any) -> t.Any:  # noqa: ANN401
    """Deserialize `obj` to a Python object.

    `obj` can be a `str`, `bytes` or `bytearray` instance containing a JSON document.
    """
    return json.loads(obj, **kwargs)
