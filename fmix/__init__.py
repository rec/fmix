from typing import Any

import tyro
from pydantic import AfterValidator


@AfterValidator
def non_negative(x: float | None):
    if x is None or x >= 0:
        return x
    raise ValueError(f'{x} is negative')


def tyro_arg(alias: str, **kwargs: Any) -> Any:
    assert alias.startswith('-'), alias
    return tyro.conf.arg(aliases=[alias], prefix_name=False)
