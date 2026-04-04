from __future__ import annotations

import dataclasses as dc
import os
from collections.abc import Sequence
from enum import StrEnum, auto
from functools import cached_property

from .curve import Curve
from .excepter import Excepter


@dc.dataclass(frozen=True)
class Files:
    inputs: Sequence[str] = ()

    # The hardcoded name of the file
    output_file: str = ''

    # A root that's used with the long common suffix in the inputs
    output_root: str = ''

    def check(self) -> None:
        with Excepter('Files') as ex:
            if bool(self.output_file) == bool(self.output_root):
                ex('Exactly one of `output_file` and  `output_root` must be given')

            ex(*(FileNotFoundError(i) for i in self.inputs if not os.path.exists(i)))
            if any(os.path.samefile(i, self.output) for i in self.inputs):
                ex(f'{self.output=} overwrites an input')

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
            with ex.catch():
                pin = Pin(self.pin)
            with ex.catch():
                curve = Curve.tri if self.curve == 'linear' else Curve(self.curve)

        self.__dict__.update(curve=curve, pin=pin)


@dc.dataclass(frozen=True)
class EditPoint:
    time: float = 0.0
    mix: dict[str, float] = dc.field(default_factory=dict)
    fade: Fade | None = None
    cut: bool = False


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

    def check(self) -> None:
        with Excepter('fmix') as ex:
            with ex.catch():
                self.files.check()
            with ex.catch():
                self.fade.check()
