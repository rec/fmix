from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from . import tyro_arg
from .curve import Curve


class Fade(BaseModel, frozen=True):
    # The curve to use for fades
    curve: Annotated[Curve, tyro_arg('-C')] = Curve.tri

    # How long fades in or out last, in seconds
    duration: Annotated[float, tyro_arg('-D')] = Field(default=1.0, ge=0.0)
