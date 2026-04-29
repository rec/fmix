from __future__ import annotations

import datetime as dt
import sys
from collections.abc import Sequence
from functools import cached_property

import numpy as np
from pydantic import BaseModel
from tuney.audio.players import DataPlayer
from tuney.audio.sample_data import SampleData

from . import audio_file
from .audio import INF, Audio, SampleRate
from .edit_point import EditPoint
from .fade import Fade
from .files import Files
from .render import render_samples


class FMix(BaseModel, frozen=True):
    audio: Audio = Audio()
    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()
    sound: bool | None = None

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
    def samplerate(self) -> SampleRate:
        return SampleRate(max(r for _, r in self.data_and_rates.values()))

    @cached_property
    def channels(self) -> int:
        return max(len(s.shape) for s, _ in self.data_and_rates.values())

    @cached_property
    def data(self) -> dict[str, np.ndarray]:
        return {k: d for k, (d, _) in self.data_and_rates.items()}

    @cached_property
    def sample_ends(self) -> list[int]:
        m = max(s.shape[0] for s, _ in self.data_and_rates.values())
        return [min(m, self.samplerate(e.seconds)) for e in self.edit_points]

    def __call__(self) -> None:
        result = self.audio(render_samples(self), self.samplerate)
        if self.files.output is None and not self.sound:
            print('Nothing to do', file=sys.stderr)
            return
        if self.files.output is not None:
            audio_file.write(self.files.output, result, self.samplerate)
        if self.sound or self.files.output is None:
            player = DataPlayer(SampleData(result, self.samplerate))
            player.run()
