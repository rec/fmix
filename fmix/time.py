from __future__ import annotations


def parse_time(t: str | float | int) -> float | int:
    if not isinstance(t, str):
        return t
    try:
        seconds, _, fraction = t.partition('.')
        parts = [int(i) for i in seconds.split(':')]
        h, m, s = (3 - len(parts)) * [0] + parts
        if fraction:
            s += float(f'0.{fraction}')
        return 3600 * h + 60 * m + s
    except Exception as e:
        raise ValueError(f'Cannot understand time {t}') from e
