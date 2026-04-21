import os
import subprocess
from collections.abc import Callable
from typing import Any

import numpy as np
import soundfile
import tdir

TEMP_FILE = 'tmp.flac'
ERRORS = 'Format not recognised', 'unable to get format from file extension'


def read(path: str) -> tuple[np.ndarray, int]:
    return _read_write(path, soundfile.read, always_2d=True)


def write(path: str, data: np.ndarray, samplerate: int) -> None:
    _read_write(path, soundfile.write, data=data, samplerate=samplerate)


def _read_write(p: str, func: Callable[..., Any], **kwargs) -> tuple[np.ndarray, int]:
    path = os.path.abspath(p)

    try:
        return func(path, **kwargs)
    except soundfile.LibsndfileError as e:
        if 'Format not recognised' not in e.error_string:
            raise
    except TypeError as e:
        if 'unable to get format from file extension' not in e.args[0]:
            raise

    with tdir.tdir():

        def convert(in_file, out_file):
            cmd = 'ffmpeg', '-i', in_file, out_file
            subprocess.run(cmd, text=True, capture_output=True)

        if func is soundfile.read:
            convert(path, TEMP_FILE)
            r = func(TEMP_FILE, **kwargs)
        else:
            r = func(TEMP_FILE, **kwargs)
            convert(TEMP_FILE, path)
        return r
