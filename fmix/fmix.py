from __future__ import annotations

import sys
from collections.abc import Collection, Sequence
from functools import cached_property
from pathlib import Path
from typing import Annotated

import numpy as np
import tomlkit
import tyro
from pydantic import BaseModel
from tuney.audio.players import DataPlayer
from tuney.audio.sample_data import SampleData

from . import audio_file, tyro_arg
from .audio import Audio, SampleRate
from .edit_point import EditPoint
from .fade import Fade
from .files import Files
from .render import render_samples

INF = float('inf')


class FMix(BaseModel, frozen=True):
    audio: Audio = Audio()

    # Load configs from a JSON or toml file
    config_file: Annotated[Path | None, tyro_arg('-c')] = None

    # Dump config as toml and exit
    dump_config: Annotated[bool, tyro_arg('-d')] = False

    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    # Play mix through speakers. If not set, play if no files.output.
    play: Annotated[tyro.conf.DisallowNone[bool | None], tyro_arg('-p')] = None

    @cached_property
    def edit_points(self) -> list[EditPoint]:
        ep = sorted(self.edit_point)
        if ep and ep[-1].mix:
            ep.append(EditPoint(time=INF))
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
        return [min(m, self.samplerate(e.time)) for e in self.edit_points]

    def __call__(self) -> None:
        if self.dump_config:
            print(dump(self))
            return

        if self.files.output is None and not self.play:
            print('Nothing to do', file=sys.stderr)
            return

        result = self.audio(render_samples(self), self.samplerate)
        if self.files.output is not None:
            audio_file.write(self.files.output, result, self.samplerate)
        if self.play or self.files.output is None:
            player = DataPlayer(SampleData(result, self.samplerate))
            player.run()


def dump(f: FMix) -> str:
    def accept(x):
        return x is not None and (not isinstance(x, (Collection, dict)) or x)

    def fix(x):
        if isinstance(x, Path):
            return str(x)
        if isinstance(x, dict):
            return {k: fix(v) for k, v in x.items() if accept(v)}
        if isinstance(x, list):
            return [fix(v) for v in x]
        return x

    d = fix(f.model_dump())
    d.pop('dump_config', None)
    d.pop('config_file', None)
    return tomlkit.dumps(d)
