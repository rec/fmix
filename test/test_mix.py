from __future__ import annotations

import tempfile
import tomllib
from pathlib import Path

from fmix import fmix

from .test_read_sample import REWRITE_TEST_DATA

ROOT = Path('test/audio')
MIX = ROOT / 'mix.m4a'


def test_mix():
    with open('test/fmix-short.toml') as fp:
        data = tomllib.loads(fp.read())

    with tempfile.NamedTemporaryFile(suffix='.m4a') as tfile:
        if (tf := Path(tfile.name)).exists():
            tf.unlink()

        if test_mix := MIX.exists() and not REWRITE_TEST_DATA:
            data['files']['output'] = tfile.name

        fmix.make_fmix(**data).run()

        if test_mix:
            actual = tf.read_bytes()
            expected = MIX.read_bytes()
            assert actual == expected
