from pathlib import Path

import soundfile as sf
from pytest import mark

FILES = sorted(str(p) for p in Path('samples/www-mmsp.ece.mcgill.ca/').glob('**/*.wav'))
BAD_FILES = [f for f in FILES if f.endswith(('voxware.wav', 'truspech.wav'))]
assert len(BAD_FILES) == 2


@mark.parametrize('filename', FILES)
def test_sample_file(filename):
    try:
        sf.read(filename)
    except sf.LibsndfileError as e:
        if filename not in BAD_FILES:
            raise
        assert 'Malformed' in e.error_string
