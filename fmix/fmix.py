from __future__ import annotations

import dataclasses as dc
import sys
from collections.abc import Sequence
from functools import cached_property
from itertools import pairwise
from typing import Any

import ffmpeg as ff
import numpy as np
from ffmpeg.nodes import InputNode

from . import audio_file
from .audio import INF, Audio, trim
from .edit_point import EditPoint
from .excepter import Excepter
from .fade import Fade
from .files import Files
from .print_invocation import print_invocation

DTYPE = 'float32'


@dc.dataclass(frozen=True)
class FMixBase:
    audio: Audio = Audio()
    edit_point: Sequence[EditPoint] = ()
    fade: Fade = Fade()
    files: Files = Files()

    @cached_property
    def edit_points(self) -> list[EditPoint]:
        ep = sorted(self.edit_point)
        if ep and ep[-1].mix:
            ep.append(EditPoint(INF, {}))
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
        return [min(length, round(self.rate * e.time_)) for e in self.edit_points]

    def render_samples(self) -> np.ndarray:
        if not self.edit_points:
            raise ValueError('No edit_points')
        length = self.sample_ends[-1] - self.sample_ends[0]
        shape = audio_file.to_shape(length, self.channels)
        result = np.zeros(shape=shape, dtype=DTYPE)
        begin = 0
        for end, ep in zip(self.sample_ends, self.edit_points, strict=True):
            F = round((ep.fade or self.fade).duration * self.rate)

            mix: np.ndarray | None = None
            for k, v in ep.mix.items():
                d = self.data[k][begin : end + F] * v
                if mix is None:
                    mix = d
                else:
                    mix += d
            if mix is None:
                continue
            mix[:F] *= np.linspace(0, 1, F, endpoint=False, dtype=DTYPE)
            mix[-F:] *= np.linspace(1, 0, F, endpoint=False, dtype=DTYPE)
            segment = result[begin : end + F]
            segment += mix[: len(segment)]
            begin = end

        return result


class FMix(FMixBase):  # DEPRECATED below here
    def render(self) -> InputNode:
        start, *rest, end = (self._stream(a, b) for a, b in pairwise(self.edit_points))
        if self.audio.fade_in:
            start = self.fade.fade(start, 'in')
        if self.audio.fade_out:
            end = self.fade.fade(end, 'out')

        stream = start
        for s in (*rest, end):
            stream = self.fade.crossfade(stream, s)
        return ff.output(stream, self.files.output)

    def run(self) -> None:
        r = self.render()
        print(print_invocation(ff.get_args(r)), file=sys.stderr)
        try:
            r.run()  # ty: ignore[unresolved-attribute]
        except ff.Error as e:
            print('ERROR from ffmpeg', e.stderr, e.stdout, sep='n')
            raise ValueError('ffmpeg error') from None
        print(self.files.output, 'written', file=sys.stdout)

    @cached_property
    def _inputs(self) -> dict[str, InputNode]:
        return {k: ff.input(v) for k, v in self.files.inputs.items()}

    def _stream(self, a: EditPoint, b: EditPoint) -> InputNode:
        ins, levels = zip(
            *((self._inputs[k], v) for k, v in a.mix.items()), strict=True
        )

        kwargs = {'start': a.time_, 'end': b.time_ + self.fade.duration}
        trimmed = [trim(i, **kwargs) for i in ins]
        formatted = [ff.filter(i, 'aformat', sample_fmts='fltp') for i in trimmed]
        weights = ' '.join(str(i) for i in levels)
        return ff.filter(formatted, 'amix', weights=weights, normalize=False)


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
