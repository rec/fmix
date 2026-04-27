from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from functools import cached_property

import numpy as np
from pydantic import BaseModel

from . import audio_file
from .audio import Audio
from .edit_point import EditPoint
from .fade import Fade
from .files import Files

INF = float('inf')


class FMix(BaseModel, frozen=True):
    audio: Audio = Audio()
    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    @cached_property
    def edit_points(self) -> list[EditPoint]:
        ep = sorted(self.edit_point)
        if ep and ep[-1].mix:
            ep.append(EditPoint(time=dt.timedelta(seconds=INF), mix={}))
        assert len(ep) > 1
        return ep

    @cached_property
    def data_and_rates(self) -> dict[str, tuple[np.ndarray, int]]:
        return {k: audio_file.read(v) for k, v in self.files.inputs.items()}

    @cached_property
    def rate(self) -> int:
        return max(r for _, r in self.data_and_rates.values())

    @cached_property
    def channels(self) -> int:
        return max(len(s.shape) for s, _ in self.data_and_rates.values())

    @cached_property
    def data(self) -> dict[str, np.ndarray]:
        return {k: d for k, (d, _) in self.data_and_rates.items()}

    @cached_property
    def sample_ends(self) -> list[int]:
        m = max(s.shape[0] for s, _ in self.data_and_rates.values())
        return [min(m, round(self.rate * e.seconds)) for e in self.edit_points]
