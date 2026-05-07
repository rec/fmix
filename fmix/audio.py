from __future__ import annotations

from typing import Annotated

import numpy as np
import tyro
from pydantic import AfterValidator, BaseModel

from .dsp import Normalize
from .time import Duration

INF = float('inf')
PRE = not True


@AfterValidator
def non_negative(x: float | None):
    if x is None or x >= 0:
        return x
    raise ValueError(f'{x} is negative')


class SampleRate(int):
    def __call__(self, time: float) -> int:
        return max(round(self * time), 0)


class Audio(BaseModel, frozen=True):
    begin: Annotated[
        Duration | None,
        non_negative,
        tyro.conf.arg(aliases=['-b'], prefix_name=PRE),
    ] = None
    end: Annotated[
        Duration | None,
        non_negative,
        tyro.conf.arg(aliases=['-e'], prefix_name=PRE),
    ] = None
    gain: Annotated[float | None, non_negative] = None
    normalize: Normalize = Normalize.normalize
    clip_fade: Annotated[float, non_negative] = 0.2

    def __call__(self, a: np.ndarray, samplerate: SampleRate) -> np.ndarray:
        a = self.normalize(a)
        F = min(samplerate(self.clip_fade), len(a) // 2)

        if self.end is not None:
            a = a[: samplerate(self.end)]
            if F:
                a[-F:] *= np.linspace(1, 0, F)
        if self.begin is not None:
            a = a[samplerate(self.begin) :]
            if F:
                a[:F] *= np.linspace(0, 1, F)
        if self.gain is not None:
            a *= self.gain
        return a
