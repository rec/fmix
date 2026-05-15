from __future__ import annotations

from typing import Annotated

import numpy as np
from pydantic import BaseModel

from . import non_negative, tyro_arg
from .constants import to_samples
from .dsp import Normalize
from .time import Duration


class Audio(BaseModel, frozen=True):
    # Start of output: None means to start from the beginning
    begin: Annotated[Duration | None, non_negative, tyro_arg('-b')] = None

    # End of output: None means to go all the way to the end
    end: Annotated[Duration | None, non_negative, tyro_arg('-e')] = None

    # How to normalize the result
    normalize: Annotated[Normalize, tyro_arg('-n')] = Normalize.normalize

    # Multiply the final result by this value after normalization
    gain: Annotated[float | None, non_negative, tyro_arg('-g')] = None

    # How to fade the begin/end clipping
    clip_fade: Annotated[float, non_negative, tyro_arg('-f')] = 0.2

    def __call__(self, a: np.ndarray) -> np.ndarray:
        a = self.normalize(a)
        F = min(to_samples(self.clip_fade), len(a) // 2)

        if self.end is not None:
            a = a[: to_samples(self.end)]
            if F:
                a[-F:] *= np.linspace(1, 0, F)
        if self.begin is not None:
            a = a[to_samples(self.begin) :]
            if F:
                a[:F] *= np.linspace(0, 1, F)
        if self.gain is not None:
            a *= self.gain
        return a
