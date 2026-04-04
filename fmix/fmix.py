from __future__ import annotations

import dataclasses as dc
import os
from collections.abc import Sequence
from enum import StrEnum, auto
from functools import cached_property
from typing import Any

from .curve import Curve
from .excepter import Excepter


@dc.dataclass(frozen=True)
class Files:
    inputs: Sequence[str] = ()

    # The hardcoded name of the file
    output_file: str = ''

    # A root that's used with the long common suffix in the inputs
    output_root: str = ''

    overwrite: bool = False

    def check(self) -> None:
        with Excepter('Files') as ex:
            if bool(self.output_file) == bool(self.output_root):
                ex('Exactly one of `output_file` and  `output_root` must be given')

            ex(*(FileNotFoundError(i) for i in self.inputs if not os.path.exists(i)))
            if os.path.exists(self.output):
                if not self.overwrite:
                    ex(FileExistsError(f'{self.output=} overwrites an existing file'))
                elif any(os.path.samefile(i, self.output) for i in self.inputs):
                    ex(FileExistsError(f'{self.output=} overwrites an input'))

    @cached_property
    def output(self) -> str:
        return self.output_file or self.output_root + os.path.commonprefix(self.inputs)


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


@dc.dataclass(frozen=True)
class Render:
    begin: float | None = None
    end: float | None = None
    gain: float = 1.0
    normalize: bool = True


@dc.dataclass(frozen=True)
class FMix:
    files: Files
    fade: Fade = Fade()
    edit_point: Sequence[EditPoint] = ()
    render: Render = Render()

    @staticmethod
    def make(
        files: dict[str, Any],
        fade: dict[str, Any],
        edit_point: list[dict[str, Any]],
        render: dict[str, Any],
        **kwargs: Any,
    ) -> FMix:
        with Excepter('FMix') as ex:
            ex(*kwargs)

            return FMix(
                files=ex.make(Files, **files),
                fade=ex.make(Fade, **fade),
                edit_point=[ex.make(EditPoint, **e) for e in edit_point],
                render=ex.make(Render, **render),
            )


# TIME_FORMATS = "%H:%M:%S.%f", "%H:%M:%S", "%M:%S.%f", "%M:%S", "%S.%f", "%S"
# This doesn't work because we want to suppose times with more than 60 seconds
# or 60 minutes.


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
