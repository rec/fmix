from __future__ import annotations

from collections.abc import Sequence
from itertools import pairwise

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from .edit_point import EditPoint, Fade

INF = float('inf')


def make_cut_points(
    edit_points: Sequence[EditPoint],
    fade: Fade,
    inputs: Sequence[InputNode],
) -> InputNode:
    edit_points = sorted(edit_points)
    if edit_points and edit_points[-1].mix:
        edit_points.append(EditPoint(INF, {}))
    assert len(edit_points) > 1

    def chunk(a: EditPoint, b: EditPoint) -> InputNode:
        ins, levels = zip((inputs[int(k)], v) for k, v in a.mix.items())
        kw = {'start': a.time_}
        if b.time_ != INF:
            kw['end'] = b.time_ + fade.duration
        trims = [i.filter('atrim', **kw) for i in ins]
        return ff.filter(trims, 'amix', weights=' '.join(str(i) for i in levels))

    stream, *streams = (chunk(a, b) for a, b in pairwise(edit_points))
    for s in streams:
        stream = fade.crossfade(stream, s)

    stream = fade.fade(stream, 'in')
    if edit_points[-1].time != INF:
        stream = fade.fade(stream, 'out')
    return stream
