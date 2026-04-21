from __future__ import annotations

import dataclasses as dc
from collections.abc import Iterator, Sequence
from functools import cached_property

from . import time
from .excepter import Excepter
from .fade import Fade


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
