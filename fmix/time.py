from __future__ import annotations


def time_to_name(time: float) -> str:
    minutes, seconds = divmod(time, 60)
    secs = str(seconds)
    hours, minutes = divmod(minutes, 60)
    if not minutes:
        return secs
    if len(secs) == 1 or secs[1] == '.':
        secs = '0' + secs
    return '{hours}:{minutes:02}:{secs}' if hours else '{minutes:02}:{secs}'


def name_to_time(time: str | float | int) -> float:
    if not isinstance(time, str):
        return float(time)

    parts = time.split(':')
    hours, minutes, seconds, *rest = [0] * (3 - len(parts)) + parts
    if rest:
        raise ValueError(f'Too many colons in {time=}')
    try:
        h, m, s = int(hours), int(minutes), float(seconds)
    except ValueError:
        raise ValueError(f"Can't understand numbers in {time=}") from None
    return 3600 * h + 60 * m + s
