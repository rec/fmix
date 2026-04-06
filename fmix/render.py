from __future__ import annotations

from itertools import pairwise

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from .audio import INF, trim
from .edit_point import EditPoint
from .fmix import FMix


def render(fm: FMix) -> InputNode:
    edit_points = sorted(fm.edit_point)
    if edit_points and edit_points[-1].mix:
        edit_points.append(EditPoint(INF, {}))
    assert len(edit_points) > 1

    begin, *streams, end = (segment(a, b, fm) for a, b in pairwise(edit_points))
    if fm.audio.fade_in:
        begin = fm.fade.fade(begin, 'in')
    if fm.audio.fade_out:
        end = fm.fade.fade(end, 'out')

    stream = begin
    for s in (*streams, end):
        stream = fm.fade.crossfade(stream, s)
    return stream


def segment(a: EditPoint, b: EditPoint, fm: FMix) -> InputNode:
    ins, levels = zip((fm.inputs[int(k)], v) for k, v in a.mix.items())

    kwargs = {'start': a.time_, 'end': b.time_ + fm.fade.duration}
    trimmed = [trim(i, **kwargs) for i in ins]
    formatted = [ff.filter(i, 'aformat', sample_fmts='fltp') for i in trimmed]
    weights = ' '.join(str(i) for i in levels)
    return ff.filter(formatted, 'amix', weights=weights, normalize=False)
