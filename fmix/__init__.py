from typing import Any

import tyro
from pydantic import AfterValidator


@AfterValidator
def non_negative(x: float | None):
    if x is None or x >= 0:
        return x
    raise ValueError(f'{x} is negative')


def tyro_arg(*aliases: str, **kwargs: Any) -> Any:
    return tyro.conf.arg(aliases=aliases, prefix_name=False)
