import os
import subprocess as sp
from pathlib import Path

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')


def run_test(cmd: str, result_file: Path | str):
    out = sp.run(cmd.split(), text=True, capture_output=True)
    assert out.stderr == ''

    result_file = Path(result_file)
    if result_file.exists() and not REWRITE_TEST_DATA:
        return result_file.read_text(), out.stdout
    else:
        result_file.write_text(out.stdout)
        return out.stdout, out.stdout
