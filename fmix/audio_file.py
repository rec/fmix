import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import tdir

from .dsp import DTYPE

_TEMP_FILE = 'tmp.wav'
ALWAYS_2D = False
TYPES = 'DOUBLE', 'FLOAT', 'PCM_32', 'PCM_24', 'PCM_16', 'MPEG_LAYER_III'


def to_shape(*a: int) -> tuple[int, ...]:
    return a if ALWAYS_2D or a[-1] != 1 else a[:-1]


def read(path: str | Path, verbose: bool = False) -> tuple[np.ndarray, int]:
    return _read_write(path, sf.read, verbose, always_2d=ALWAYS_2D, dtype=DTYPE)


def write(
    path: str | Path, data: np.ndarray, samplerate: int, verbose: bool = False
) -> None:
    _read_write(path, sf.write, verbose, data=data, samplerate=samplerate)


def _read_write(
    p: str | Path, func: Callable[..., Any], verbose: bool, **kwargs: Any
) -> tuple[np.ndarray, int]:
    p = Path(p)
    fmt = p.suffix[1:].upper()
    is_write = func is sf.write
    if fmt in sf.available_formats():
        if is_write:
            subs = sf.available_subtypes(fmt)
            kwargs['subtype'] = next(t for t in TYPES if t in subs)
        return func(p, **kwargs)

    def convert(in_file, out_file):
        cmd = 'ffmpeg', '-i', in_file, out_file
        if verbose:
            print('$', *cmd, file=sys.stderr)
        subprocess.run(cmd, text=True, capture_output=True)

    path = os.path.abspath(p)
    with tdir.tdir():
        if not is_write:
            convert(path, _TEMP_FILE)
        r = func(_TEMP_FILE, **kwargs)
        if is_write:
            convert(_TEMP_FILE, path)
        return r
