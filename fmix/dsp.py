import numpy as np

DTYPE = np.float64


def normalize(data: np.ndarray, mutate: bool = True, expand: bool = True) -> np.ndarray:
    assert np.issubdtype(data.dtype, np.floating)
    scale = max(abs(data.max()), abs(data.min()))
    if scale != 1.0 and (expand or scale > 1.0):
        if mutate:
            data /= scale
        else:
            data = data / scale
    return data


def to_float(data: np.ndarray) -> np.ndarray:
    if np.issubdtype(data.dtype, np.floating):
        return data
    ii = np.iinfo(data.dtype)
    return data / max(-float(ii.min), float(ii.max))


def to_integer(data: np.ndarray, dtype=DTYPE) -> np.ndarray:
    if np.issubdtype(data.dtype, np.integer):
        return data
    ii = np.iinfo(dtype)
    d = data * max(-float(ii.min), float(ii.max))
    np.clip(d, a_min=float(ii.min), a_max=float(ii.max), out=d)
    return d.astype(dtype)
