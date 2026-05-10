from __future__ import annotations

from typing import Annotated

from annotated_types import Ge
from pydantic import BaseModel, Field

from .fade import Fade


class EditPoint(BaseModel, frozen=True):
    # The time in seconds for this edit point
    time: Annotated[float, Ge(0)]
    mix: dict[str, Annotated[float, Ge(0)]] = Field(default_factory=dict)
    fade: Fade | None = None

    def __lt__(self, other: EditPoint) -> bool:
        return self.time < other.time
