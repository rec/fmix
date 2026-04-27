from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from fmix import fmix

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
TEST_DIR = Path(__file__).parent


def make_fmix(name: str) -> fmix.FMix:
    return _make_fmix(name)[0]


def _make_fmix(name: str) -> tuple[fmix.FMix, dict[str, Any]]:
    with open(TEST_DIR / f'{name}.toml') as fp:
        data = tomllib.loads(fp.read())

    return fmix.make_fmix(**data), data
