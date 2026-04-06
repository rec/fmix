from __future__ import annotations

import dataclasses as dc
import os
from collections.abc import Sequence
from functools import cached_property
from typing import Any

from .edit_point import EditPoint, Fade
from .excepter import Excepter


@dc.dataclass(frozen=True)
class Files:
    inputs: Sequence[str] = ()

    # The hardcoded name of the file
    output_file: str = ''

    # A root that's used with the long common suffix in the inputs
    output_root: str = ''

    overwrite: bool = False

    def check(self) -> None:
        with Excepter('Files') as ex:
            if bool(self.output_file) == bool(self.output_root):
                ex('Exactly one of `output_file` and  `output_root` must be given')

            ex(*(FileNotFoundError(i) for i in self.inputs if not os.path.exists(i)))
            if os.path.exists(self.output):
                if not self.overwrite:
                    ex(FileExistsError(f'{self.output=} overwrites an existing file'))
                elif any(os.path.samefile(i, self.output) for i in self.inputs):
                    ex(FileExistsError(f'{self.output=} overwrites an input'))

    @cached_property
    def output(self) -> str:
        return self.output_file or self.output_root + os.path.commonprefix(self.inputs)


@dc.dataclass(frozen=True)
class Audio:
    begin: float | None = None
    end: float | None = None
    gain: float = 1.0
    normalize: bool = True
    fade_in: bool = True
    fade_out: bool = True


@dc.dataclass(frozen=True)
class FMix:
    audio: Audio = Audio()
    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    @staticmethod
    def make(**kwargs: Any) -> FMix:
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
