from __future__ import annotations

import dataclasses as dc
import os
from collections.abc import Sequence
from enum import StrEnum, auto
from functools import cached_property


@dc.dataclass(frozen=True)
class Files:
    input_files: Sequence[str] = ()

    # The hardcoded name of the file
    file_name: str = ''

    # A root that's used with the long common suffix in the inputs
    file_root: str = ''

    @cached_property
    def output_file(self) -> str:
        if bool(self.file_name) == bool(self.file_root):
            raise ValueError('Exactly one of `file_name` and  file_root` must be given')
        return self.file_name or self.file_root + os.path.commonprefix(self.input_files)


class Pin(StrEnum):
    """Where the time at an edit point is attached to in the fade"""

    begin = auto()
    middle = auto()
    end = auto()


@dc.dataclass(frozen=True)
class Fade:
    shape: str = 'linear'
    duration: float = 1.0
    pin: Pin = Pin.middle


@dc.dataclass(frozen=True)
class EditPoint:
    time: float = 0.0
    mix: dict[str, float] = dc.field(default_factory=dict)
    fade: Fade | None = None
    cut: bool = False


@dc.dataclass(frozen=True)
class FMix:
    files: Files
    fade: Fade = Fade()
    edit_points: Sequence[EditPoint] = ()
