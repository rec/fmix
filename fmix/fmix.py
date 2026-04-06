from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from itertools import pairwise
from typing import Any

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from .audio import INF, Audio, trim
from .edit_point import EditPoint, Fade
from .excepter import Excepter
from .files import Files


@dc.dataclass(frozen=True)
class FMix:
    audio: Audio = Audio()
    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    def render(self) -> InputNode:
        edit_points = sorted(self.edit_point)
        if edit_points and edit_points[-1].mix:
            edit_points.append(EditPoint(INF, {}))
        assert len(edit_points) > 1

        begin, *streams, end = (self._stream(a, b) for a, b in pairwise(edit_points))
        if self.audio.fade_in:
            begin = self.fade.fade(begin, 'in')
        if self.audio.fade_out:
            end = self.fade.fade(end, 'out')

        stream = begin
        for s in (*streams, end):
            stream = self.fade.crossfade(stream, s)
        return ff.output(stream, self.files.output)

    @cached_property
    def _inputs(self) -> Sequence[InputNode]:
        return [ff.input(f'"{i}"') for i in self.files.inputs]

    def _stream(self, a: EditPoint, b: EditPoint) -> InputNode:
        ins, levels = zip(
            *((self._inputs[int(k)], v) for k, v in a.mix.items()), strict=True
        )

        kwargs = {'begin': a.time_, 'end': b.time_ + self.fade.duration}
        trimmed = [trim(i, **kwargs) for i in ins]
        formatted = [ff.filter(i, 'aformat', sample_fmts='fltp') for i in trimmed]
        weights = ' '.join(str(i) for i in levels)
        return ff.filter(formatted, 'amix', weights=weights, normalize=False)


def make_fmix(**kwargs: Any) -> FMix:
    with Excepter('FMix') as ex:
        missing = [f.name for f in dc.fields(FMix) if f.name not in kwargs]
        ex(*(f'Missing field {i}' for i in missing))
        kwargs |= {k: {} for k in missing}

        audio = ex.make(Audio, **kwargs.pop('audio'))
        edit_point = [ex.make(EditPoint, **e) for e in kwargs.pop('edit_point')]
        files = ex.make(Files, **kwargs.pop('files'))
        fade = ex.make(Fade, **kwargs.pop('fade'))
        ex(*(f'Unknown field: {k}' for k in kwargs))

        return FMix(audio=audio, fade=fade, files=files, edit_point=edit_point)
