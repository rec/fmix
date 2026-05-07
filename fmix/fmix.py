from __future__ import annotations

import json
import sys
import tomllib
from collections.abc import Iterator, Sequence
from functools import cached_property
from pathlib import Path
from typing import Annotated, Any, TypeIs

import numpy as np
import tyro
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

    config_file: Annotated[
        Path | None,
        tyro.conf.arg(aliases=['-c'], help='Load configs from a JSON or toml file'),
    ] = None

    dump_config: Annotated[
        bool,
        tyro.conf.arg(aliases=['-d'], help='Dump config as toml'),
    ] = False

    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    play: Annotated[
        bool | None,
        tyro.conf.arg(
            aliases=['-p'],
            help='Play mix through speakers. If not set, play if no files.output',
        ),
    ] = None

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
        result = self.audio(render_samples(self), self.samplerate)
        if self.files.output is None and not self.play:
            print('Nothing to do', file=sys.stderr)
            return
        if self.files.output is not None:
            audio_file.write(self.files.output, result, self.samplerate)
        if self.play or self.files.output is None:
            player = DataPlayer(SampleData(result, self.samplerate))
            player.run()

    @staticmethod
    def from_tyro(**kwargs: Any) -> FMix:
        fmix = tyro.cli(FMix, **kwargs)
        if fmix.config_file:
            fmix = tyro.cli(FMix, default=read_fmix(fmix.config_file), **kwargs)
        return fmix


def is_str_dict(x: Any) -> TypeIs[dict[str, Any]]:
    return isinstance(x, dict) and all(isinstance(k, str) for k in x.keys())


def read_file(path: Path) -> dict[str, Any]:
    data = path.read_text()
    match path.suffix:
        case '.toml':
            result = tomllib.loads(data)
        case '.json':
            result = json.loads(data)
        case _:
            raise ValueError(f'Do not understand file {path}')
    if not is_str_dict(result):
        raise ValueError(f'File {path} does not contain a string dictionary')
    return result


def read_fmix(path: Path) -> FMix:
    return FMix(**read_file(path))


def dict_keys(d: dict[str, Any], *keys: str) -> Iterator[tuple[str, ...]]:
    # Delete if tyro does its schtuff
    for k, v in d.items():
        if isinstance(v, dict):
            yield from dict_keys(v, *keys, k)
        else:
            yield (*keys, k)
