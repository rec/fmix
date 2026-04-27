from __future__ import annotations

import datetime as dt
from typing import Annotated

from pydantic import AfterValidator, BaseModel


def non_negative[T](x: T) -> T:
    if x is None:
        return x
    if isinstance(x, (int, float)):
        seconds = x
    elif isinstance(x, dt.timedelta):
        seconds = x.total_seconds()
    else:
        raise TypeError(f'{x=} {type(x)=}')
    if seconds < 0:
        raise ValueError(f'{x} is negative')
    return x


class Audio(BaseModel, frozen=True):
    start: Annotated[dt.timedelta | None, AfterValidator(non_negative)] = None
    end: Annotated[dt.timedelta | None, AfterValidator(non_negative)] = None
    gain: Annotated[float, AfterValidator(non_negative)] = 1.0
    normalize: bool = True
    fade_in: bool = True  # Not in use
    fade_out: bool = True  # Not in use
