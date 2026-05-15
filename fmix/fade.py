from __future__ import annotations

from functools import cached_property
from typing import Annotated

import numpy as np
from pydantic import BaseModel, Field

from . import non_negative, tyro_arg
from .constants import dtype, to_samples


class Fade(BaseModel, frozen=True):
    # The polynomial exponent for the base curve.
    exponent: Annotated[float, non_negative] = 1.0

    # If False, mix using equal power curve
    equal_voltage: bool = False

    # How long fades in or out last, in seconds
    duration: Annotated[float, tyro_arg('-D')] = Field(default=1.0, ge=0.0)

    @cached_property
    def crossfade(self) -> tuple[np.ndarray, np.ndarray]:
        f = self.fade_in
        return (f, 1 - f) if self.equal_voltage else (f**0.5, (1 - f) ** 0.5)

    @cached_property
    def fade_in(self) -> np.ndarray:
        return self._fade(0, 1)

    @cached_property
    def fade_out(self) -> np.ndarray:
        return self._fade(1, 0)

    @cached_property
    def num_samples(self) -> int:
        return to_samples(self.duration)

    def _fade(self, begin: float, end: float) -> np.ndarray:
        a = np.linspace(begin, end, self.num_samples, dtype=dtype())
        return a if self.exponent == 1.0 else np.pow(a, self.exponent, out=a)
