from __future__ import annotations

import dataclasses as dc

import ffmpeg as ff
from ffmpeg.nodes import InputNode


@dc.dataclass(frozen=True)
class Audio:
    start: float | None = None
    end: float | None = None
    gain: float = 1.0
    normalize: bool = True
    fade_in: bool = True
    fade_out: bool = True


INF = float('inf')


def trim(
    a: InputNode, start: float | None = None, end: float | None = None
) -> InputNode:
    kwargs = {}
    if start is not None and start > 0:
        kwargs['start'] = start
    if end is not None and end != INF:
        kwargs['end'] = end

    return ff.filter(a, 'atrim', **kwargs) if kwargs else a
