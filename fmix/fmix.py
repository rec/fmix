from __future__ import annotations

import sys
from collections.abc import Collection
from functools import cached_property
from pathlib import Path
from typing import Annotated

import numpy as np
import tomlkit
import tyro
from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from tuney.audio.device import Device
from tuney.audio.players import DataPlayer
from tuney.audio.sample_data import SampleData

from . import audio_file, constants, tyro_arg
from .audio import Audio
from .edit_point import EditPoint
from .fade import Fade
from .files import Files
from .render import render_samples

INF = float('inf')


@AfterValidator
def validate_end_points(ep: list[EditPoint]) -> list[EditPoint]:
    ep.sort()
    if ep and ep[-1].mix:
        # If the last point isn't an empty mix, add a segment going all the way
        # to the end.
        ep.append(EditPoint(time=INF))
    return ep


class FMix(BaseModel, frozen=True):
    """
    🎧 fmix: Quickly mix a recording session from the command line 🎧

    Balance and crossfade mixes of existing tracks, like those captured from a digital
    mixer during performance, based on a text file description in JSON or TOML.

    Handles either stereo or mono sources.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Load configs from a JSON or toml file
    config_file: Annotated[Path | None, tyro.conf.Positional] = None

    audio: Audio = Audio()
    device: int | str | None = None

    dtype: Annotated[str, tyro_arg('-t')] = 'float64'

    # Dump config as toml and exit
    dump_config: Annotated[bool, tyro_arg('-d')] = False

    edit_points: Annotated[
        list[EditPoint],
        validate_end_points,
        tyro.conf.UsePythonSyntaxForLiteralCollections,
    ] = Field(default_factory=list)
    fade: Fade = Fade()
    files: Files = Files()

    # Play mix through speakers. If not set, play if no files.output.
    play: Annotated[tyro.conf.DisallowNone[bool | None], tyro_arg('-p')] = None

    # Print more information
    verbose: Annotated[bool, tyro_arg('-v')] = False

    @cached_property
    def channels(self) -> int:
        return max(len(d.shape) for d in self.data.values())

    @cached_property
    def data(self) -> dict[str, np.ndarray]:
        return self._samplerate_data[1]

    @cached_property
    def samplerate(self) -> int:
        return self._samplerate_data[0]

    def __call__(self) -> str | None:
        constants.set_samplerate(self.samplerate)
        constants.set_dtype(self.dtype)

        if self.dump_config:
            print(dump(self))
            return
        if self.files.output is None and self.play is False:
            return 'Nothing to do'
        if self.verbose:
            print(dump(self), file=sys.stderr)

        result = self.audio(render_samples(self, self.dtype))
        if self.files.output is not None:
            audio_file.write(self.files.output, result, self.verbose)
        if self.play or self.files.output is None:
            device = Device(
                channels=self.channels,
                device=self.device,
                dtype=self.dtype,
                samplerate=self.samplerate,
            )
            player = DataPlayer(SampleData(result, self.samplerate), device=device)
            player.run()

    @cached_property
    def _samplerate_data(self) -> tuple[int, dict[str, np.ndarray]]:
        it = self.files.inputs.items()
        ds = {k: audio_file.read(v, self.dtype, self.verbose) for k, v in it}
        samplerate = max(s for _, s in ds.values())
        return samplerate, {k: d for k, (d, _) in ds.items()}


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
