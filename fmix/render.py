from __future__ import annotations

from itertools import pairwise

import numpy as np

from fmix import audio_file
from fmix.dsp import DTYPE
from fmix.fmix import FMix


def render_samples(fmix: FMix) -> np.ndarray:
    if not fmix.edit_points:
        raise ValueError('No edit_points')

    length = fmix.sample_ends[-1] - fmix.sample_ends[0]
    shape = audio_file.to_shape(length, fmix.channels)
    result = np.zeros(shape=shape, dtype=DTYPE)

    begin_end = pairwise([0] + fmix.sample_ends)
    for (begin, end), ep in zip(begin_end, fmix.edit_points, strict=True):
        if not ep.mix:
            continue

        F = round((ep.fade or fmix.fade).duration * fmix.rate)
        mix: np.ndarray | None = None
        for k, v in ep.mix.items():
            d = fmix.data[k][begin : end + F] * v
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

    return result
