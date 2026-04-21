from __future__ import annotations

import dataclasses as dc
from collections.abc import Iterator, Sequence
from functools import cached_property

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from . import time
from .curve import Curve
from .excepter import Excepter


@dc.dataclass(frozen=True)
class Fade:
    curve: Curve = Curve.tri
    duration: float = 1.0  # Negative means a gap!

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
    time: float | int | str
    mix: dict[str, float]
    fade: Fade | None = None  # in, out and crossfade!

    @cached_property
    def time_(self) -> float:
        return time.name_to_time(self.time)

    def check(self) -> None:
        with Excepter('EditPoint') as ex:
            ex.call(lambda: self.time_)

    def __lt__(self, other: EditPoint) -> bool:
        return self.time_ < other.time_


@dc.dataclass(frozen=True)
class Edit:
    edit_point: EditPoint
    start: float
    fade: Fade


def edits(edit_points: Sequence[EditPoint], fade: Fade) -> Iterator[Edit]:
    start = edit_points[0].time_
    for ep in edit_points:
        yield Edit(ep, ep.time_ - start, ep.fade or fade)
