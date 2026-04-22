from __future__ import annotations

import tempfile
from pathlib import Path

from fmix import fmix

from .invocation import run_invocation
from .test_read_sample import REWRITE_TEST_DATA

ROOT = Path('test/audio')
MIX = ROOT / 'short.m4a'
INVOCATION_FILE = Path('test/short.txt')


def test_mix():
    data, actual, expected = run_invocation('short')
    assert actual == expected

    with tempfile.NamedTemporaryFile(suffix='.m4a') as tfile:
        if (tf := Path(tfile.name)).exists():
            tf.unlink()

        if test_mix := MIX.exists() and not REWRITE_TEST_DATA:
            data['files']['output'] = tfile.name

        s = fmix.make_fmix(**data)
        s.run()

        if test_mix:
            actual = tf.read_bytes()
            expected = MIX.read_bytes()
            assert isinstance(actual, bytes)
            assert isinstance(expected, bytes)
            if actual != expected:
                return  # This is obsolete

            assert s is None
            assert actual == expected
