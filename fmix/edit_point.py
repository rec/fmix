from __future__ import annotations

import dataclasses as dc
from enum import StrEnum, auto
from functools import cached_property

from fmix.curve import Curve
from fmix.excepter import Excepter


class Pin(StrEnum):
    """Where the time at an edit point is attached to in the fade"""

    begin = auto()
    middle = auto()
    end = auto()


@dc.dataclass(frozen=True)
class Fade:
    curve: Curve = Curve.tri
    duration: float = 1.0
    pin: Pin = Pin.middle

    def check(self) -> None:
        with Excepter('Fade') as ex:
            ex.call(Pin, self.pin)
            if self.curve == 'linear':
                self.__dict__['curve'] = Curve.tri
            else:
                ex.call(Curve, self.curve)


@dc.dataclass(frozen=True)
class EditPoint:
    time: float | str = 0.0
    mix: dict[str, float] = dc.field(default_factory=dict)
    fade: Fade | None = None
    cut: bool = False

    def __lt__(self, other: EditPoint) -> bool:
        return self.time_ < other.time_

    def check(self) -> None:
        with Excepter('EditPoint') as ex:
            ex.call(lambda: self.time_)

    @cached_property
    def time_(self) -> float:
        return _parse_time(self.time)


def _parse_time(t: str | float | int) -> float | int:
    if not isinstance(t, str):
        return t
    try:
        seconds, _, fraction = t.partition('.')
        parts = [int(i) for i in seconds.split(':')]
        h, m, s = (3 - len(parts)) * [0] + parts
        if fraction:
            s += float(f'0.{fraction}')
        return 3600 * h + 60 * m + s
    except Exception as e:
        raise ValueError(f'Cannot understand time {t}') from e
