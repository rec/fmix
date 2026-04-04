from __future__ import annotations

import dataclasses as dc
import os
from enum import StrEnum, auto


@dc.dataclass(frozen=True)
class Out:
    # The hardcoded name of the file
    file_name: str = ""

    # A root that's used with the long common suffix in the inputs
    file_root: str = ""

    def __post_init__(self) -> None:
        if bool(self.file_name) == bool(self.file_root):
            raise ValueError("Exactly one of `file_name` and  file_root` must be given")

    def __call__(self, *files: str) -> str:
        return self.file_name or self.file_root + os.path.commonprefix(files)


class Pin(StrEnum):
    """Where the time at an edit point is attached to in the fade"""

    begin = auto()
    middle = auto()
    end = auto()


@dc.dataclass(frozen=True)
class Fade:
    shape: str = "linear"
    duration: float = 1.0
    pin: Pin = Pin.middle


@dc.dataclass(frozen=True)
class EditPoint:
    time: float
    mix: dict[str, float] = dc.field(default_factory=dict)
    fade: Fade | None = None
