from __future__ import annotations

import dataclasses as dc
from functools import cached_property

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from fmix.curve import Curve
from fmix.excepter import Excepter
from fmix.time import parse_time


@dc.dataclass(frozen=True)
class Fade:
    curve: Curve = Curve.tri
    duration: float = 1.0

    def crossfade(self, a: InputNode, b: InputNode) -> InputNode:
        c, d = self.curve, self.duration
        return ff.filter((a, b), 'acrossfade', curve1=c, curve2=c, duration=d)

    def fade(self, a: InputNode, type_: str) -> InputNode:
        return ff.filter(a, 'afade', type=type_, duration=self.duration)

    def check(self) -> None:
        with Excepter('Fade') as ex:
            if self.curve == 'linear':
                self.__dict__['curve'] = Curve.tri
            else:
                ex.call(Curve, self.curve)


@dc.dataclass(frozen=True)
class EditPoint:
    time: float | str
    mix: dict[str, float]

    @cached_property
    def time_(self) -> float:
        return parse_time(self.time)

    def check(self) -> None:
        with Excepter('EditPoint') as ex:
            ex.call(lambda: self.time_)

    def __lt__(self, other: EditPoint) -> bool:
        return self.time_ < other.time_
