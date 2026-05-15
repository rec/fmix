def dtype() -> str:
    assert _dtype is not None
    return _dtype


def set_dtype(dtype: str):
    global _dtype

    assert _dtype in (None, dtype), (_dtype, dtype)
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


_dtype: str | None = None
_samplerate: int | None = None
