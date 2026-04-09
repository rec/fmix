import sys
from typing import Iterator, Sequence


def print_invocation(args: Sequence[str]) -> str:
    def it() -> Iterator[str]:
        is_filter = False
        yield 'ffmpeg'
        for v in args:
            if v.startswith('-'):
                is_filter = v == '-filter_complex'
                yield f' \\\n {v}'
            elif is_filter:
                yield ' '
                for i, f in enumerate(v.split(';')):
                    if i:
                        yield ';'
                    yield f'\\\n{f}'
            else:
                yield ' '
                yield v
        yield '\n'


    return ''.join(it())
