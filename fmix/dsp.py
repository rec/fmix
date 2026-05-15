from enum import StrEnum, auto

import numpy as np


class Normalize(StrEnum):
    none = auto()
    limit = auto()
    normalize = auto()

    def __call__(self, data: np.ndarray, mutate: bool = True) -> np.ndarray:
        assert np.issubdtype(data.dtype, np.floating)
        if self != Normalize.none:
            scale = max(abs(data.max()), abs(data.min()))
            if scale != 1.0 and (self.normalize or scale > 1.0):
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


def to_integer(data: np.ndarray, dtype: np.dtype) -> np.ndarray:
    if np.issubdtype(data.dtype, np.integer):
        return data
    ii = np.iinfo(dtype)
    d = data * max(-float(ii.min), float(ii.max))
    np.clip(d, a_min=float(ii.min), a_max=float(ii.max), out=d)
    return d.astype(dtype)
