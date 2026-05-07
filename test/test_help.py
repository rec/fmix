from __future__ import annotations

import os
import subprocess as sp
from pathlib import Path

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
RESULT_FILE = Path('test/help.txt')


def test_help():
    out = sp.run(('fmix', '-h'), text=True, capture_output=True)
    assert out.stderr == ''

    if RESULT_FILE.exists() and not REWRITE_TEST_DATA:
        assert out.stdout == RESULT_FILE.read_text()
    else:
        RESULT_FILE.write_text(out.stdout)
