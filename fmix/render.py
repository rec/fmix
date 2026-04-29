from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

import numpy as np

from fmix import audio_file
from fmix.dsp import DTYPE

if TYPE_CHECKING:
    from fmix.fmix import FMix


def render_samples(f: FMix) -> np.ndarray:
    if not f.edit_points:
        raise ValueError('No edit_points')

    length = f.sample_ends[-1] - f.sample_ends[0]
    shape = audio_file.to_shape(length, f.channels)
    result = np.zeros(shape=shape, dtype=DTYPE)

    begin_end = pairwise([0] + f.sample_ends)
    for (begin, end), ep in zip(begin_end, f.edit_points, strict=True):
        if not ep.mix:
            continue

        F = f.samplerate((ep.fade or f.fade).duration)
        mix: np.ndarray | None = None
        for k, v in ep.mix.items():
            d = f.data[k][begin : end + F] * v
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

    return f.audio(result, f.samplerate)
