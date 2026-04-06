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
    fade_in: bool = True,
    fade_out: bool = True,
) -> InputNode:
    edit_points = sorted(edit_points)
    if edit_points and edit_points[-1].mix:
        edit_points.append(EditPoint(INF, {}))
    assert len(edit_points) > 1

    def segment(a: EditPoint, b: EditPoint) -> InputNode:
        ins, levels = zip((inputs[int(k)], v) for k, v in a.mix.items())

        kwargs = {'start': a.time_}
        if b.time_ != INF:
            kwargs['end'] = b.time_ + fade.duration
        trimmed = [ff.filter(i, 'atrim', **kwargs) for i in ins]
        formatted = [ff.filter(i, 'aformat', sample_fmts='fltp') for i in trimmed]
        weights = ' '.join(str(i) for i in levels)
        return ff.filter(formatted, 'amix', weights=weights, normalize=False)

    begin, *streams, end = (segment(a, b) for a, b in pairwise(edit_points))
    if fade_in:
        begin = fade.fade(begin, 'in')
    if fade_out:
        end = fade.fade(end, 'out')

    stream = begin
    for s in (*streams, end):
        stream = fade.crossfade(stream, s)
    return stream
