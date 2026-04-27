from __future__ import annotations

from pydantic import BaseModel


class Audio(BaseModel, frozen=True):
    start: float | None = None
    end: float | None = None
    gain: float = 1.0
    normalize: bool = True
    fade_in: bool = True  # Not in use
    fade_out: bool = True  # Not in use
