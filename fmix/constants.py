import numpy as np


def dtype() -> np.dtype | None:
    return _dtype


def set_dtype(dtype: np.dtype) -> np.dtype | None:
    global _dtype
    assert _dtype is None or _dtype == dtype
    _dtype = dtype


def samplerate() -> int:
    assert _samplerate is not None
    return _samplerate


def set_samplerate(samplerate: int):
    global _samplerate

    assert _samplerate in (None, samplerate), (_samplerate, samplerate)
    _samplerate = samplerate


def to_samples(time: float) -> int:
    return round(samplerate() * time)


_dtype: np.dtype | None = None
_samplerate: int | None = None
