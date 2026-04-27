from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from functools import cached_property

import numpy as np
from pydantic import BaseModel

from . import audio_file
from .audio import Audio
from .dsp import DTYPE
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
        # TODO: convert integer samples to float!
        # TODO: convert sample rates
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
        length = max(s.shape[0] for s, _ in self.data_and_rates.values())
        return [min(length, round(self.rate * e.seconds)) for e in self.edit_points]

    def render_samples(self) -> np.ndarray:
        if not self.edit_points:
            raise ValueError('No edit_points')
        length = self.sample_ends[-1] - self.sample_ends[0]
        shape = audio_file.to_shape(length, self.channels)
        result = np.zeros(shape=shape, dtype=DTYPE)
        begin = 0
        for end, ep in zip(self.sample_ends, self.edit_points, strict=True):
            if ep.mix:
                self.render_sample(begin, end, ep, result)
            begin = end
        return result

    def render_sample(
        self, begin: int, end: int, ep: EditPoint, result: np.ndarray
    ) -> None:
        F = round((ep.fade or self.fade).duration * self.rate)

        mix: np.ndarray | None = None
        for k, v in ep.mix.items():
            d = self.data[k][begin : end + F] * v
            if mix is None:
                mix = d
            else:
                mix += d
        assert mix is not None
        if F:
            mix[:F] *= np.linspace(0, 1, F, endpoint=False, dtype=DTYPE)
            mix[-F:] *= np.linspace(1, 0, F, endpoint=False, dtype=DTYPE)
        segment = result[begin : end + F]
        segment += mix[: len(segment)]
