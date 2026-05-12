from typing import Any

import numpy as np
import tyro
from pydantic import AfterValidator

DTYPE = np.float64


@AfterValidator
def non_negative(x: float | None):
    if x is None or x >= 0:
        return x
    raise ValueError(f'{x} is negative')


def tyro_arg(alias: str, **kwargs: Any) -> Any:
    assert alias.startswith('-'), alias
    return tyro.conf.arg(aliases=[alias], prefix_name=False)


def samplerate() -> int:
    assert _samplerate is not None
    return _samplerate


def set_samplerate(samplerate: int):
    global _samplerate

    assert _samplerate in (None, samplerate), (_samplerate, samplerate)
    _samplerate = samplerate


def to_samples(time: float) -> int:
    return round(samplerate() * time)


_samplerate = None
