from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

import numpy as np

from fmix import audio_file

from .constants import to_samples

if TYPE_CHECKING:
    from fmix.fmix import FMix


def render_samples(f: FMix, dtype: str) -> np.ndarray:
    m = max(d.shape[0] for d in f.data.values())
    sample_ends = [min(m, to_samples(e.time)) for e in f.edit_points]

    length = sample_ends[-1] - sample_ends[0]
    shape = audio_file.to_shape(length, f.channels)
    result = np.zeros(shape=shape, dtype=dtype)

    bep = zip(pairwise([0] + sample_ends), f.edit_points, strict=True)
    last = len(f.edit_points) - 1
    for i, ((begin, end), ep) in enumerate(bep):
        if not ep.mix:
            continue

        fade = ep.fade or f.fade
        F = fade.num_samples
        mix: np.ndarray | None = None
        for k, v in ep.mix.items():
            d = f.data[k][begin : end + F] * v
            if mix is None:
                mix = d
            else:
                mix += d
        assert mix is not None
        if F:
            mix[:F] *= fade.fade_in if i == 0 else fade.crossfade[0]
            mix[-F:] *= fade.fade_out if i == last else fade.crossfade[1]

        segment = result[begin : end + F]
        segment += mix[: len(segment)]

    return f.audio(result)
