import os
import subprocess
from collections.abc import Callable
from typing import Any

import numpy as np
import soundfile as sf
import tdir

TEMP_FILE = 'tmp.wav'
ALWAYS_2D = False
DTYPE = 'float32'


def to_shape(*a: int) -> tuple[int, ...]:
    return a if ALWAYS_2D or a[-1] != 1 else a[:-1]


def read(path: str) -> tuple[np.ndarray, int]:
    return _read_write(path, sf.read, always_2d=ALWAYS_2D, dtype=DTYPE)


def write(path: str, data: np.ndarray, samplerate: int) -> None:
    _read_write(path, sf.write, data=data, samplerate=samplerate, subtype='FLOAT')


def _read_write(
    p: str, func: Callable[..., Any], **kwargs: Any
) -> tuple[np.ndarray, int]:
    if str(p).endswith('.wav'):
        return func(p, **kwargs)

    def convert(in_file, out_file):
        cmd = 'ffmpeg', '-i', in_file, out_file
        subprocess.run(cmd, text=True, capture_output=True)

    path = os.path.abspath(p)
    with tdir.tdir():
        if func is sf.read:
            convert(path, TEMP_FILE)
        r = func(TEMP_FILE, **kwargs)
        if func is not sf.read:
            convert(TEMP_FILE, path)
        return r
