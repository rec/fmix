from __future__ import annotations

import dataclasses as dc
from collections.abc import Sequence
from functools import cached_property
from typing import Any

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from .audio import Audio
from .edit_point import EditPoint, Fade
from .excepter import Excepter
from .files import Files


@dc.dataclass(frozen=True)
class FMix:
    audio: Audio = Audio()
    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    @cached_property
    def inputs(self) -> Sequence[InputNode]:
        return [ff.input(i) for i in self.files.inputs]


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
