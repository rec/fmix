from __future__ import annotations

from pydantic import BaseModel, Field

from .curve import Curve


class Fade(BaseModel, frozen=True):
    curve: Curve = Curve.tri
    duration: float = Field(default=1.0, ge=0.0)
