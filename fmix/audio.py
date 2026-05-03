from __future__ import annotations

import datetime as dt
from typing import Annotated

import numpy as np
from pydantic import AfterValidator, BaseModel
import tyro

from .dsp import Normalize
from .time import name_to_time

INF = float('inf')


@AfterValidator
def non_negative(x: float | dt.timedelta | None):
    if x is not None and _to_seconds(x) < 0:
        raise ValueError(f'{x} is negative')
    return x


to_timedelta = tyro.conf.arg(constructor=name_to_time)

class SampleRate(int):
    def __call__(self, time: float | dt.timedelta) -> int:
        return max(round(self * _to_seconds(time)), 0)


class Audio(BaseModel, frozen=True):
    begin: Annotated[dt.timedelta | None, non_negative, to_timedelta] = None
    end: Annotated[dt.timedelta | None, non_negative, to_timedelta] = None
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


def _to_seconds(x: float | dt.timedelta) -> float:
    return x.total_seconds() if isinstance(x, dt.timedelta) else x
