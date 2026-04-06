from __future__ import annotations

import dataclasses as dc
from functools import cached_property

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from fmix.curve import Curve
from fmix.excepter import Excepter

INF = float('inf')


def trim(
    a: InputNode, begin: float | None = None, end: float | None = None
) -> InputNode:
    kwargs = {}
    if begin is not None and begin > 0:
        kwargs['begin'] = begin
    if end is not None and end != INF:
        kwargs['end'] = end

    return ff.filter(a, 'atrim', **kwargs) if kwargs else a


@dc.dataclass(frozen=True)
class Fade:
    curve: Curve = Curve.tri
    duration: float = 1.0

    def crossfade(self, a: InputNode, b: InputNode) -> InputNode:
        c, d = self.curve, self.duration
        return ff.filter((a, b), 'acrossfade', curve1=c, curve2=c, duration=d)

    def fade(self, a: InputNode, type_: str) -> InputNode:
        return ff.filter(a, 'afade', type=type_, duration=self.duration, normalize=0)

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
        return _parse_time(self.time)

    def check(self) -> None:
        with Excepter('EditPoint') as ex:
            ex.call(lambda: self.time_)

    def __lt__(self, other: EditPoint) -> bool:
        return self.time_ < other.time_


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
