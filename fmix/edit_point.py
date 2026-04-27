from __future__ import annotations

from datetime import timedelta
from functools import cached_property
from typing import Annotated

from annotated_types import Ge
from pydantic import BaseModel

from .fade import Fade


class EditPoint(BaseModel, frozen=True):
    time: timedelta
    mix: dict[str, Annotated[float, Ge(0)]]
    fade: Fade | None = None

    @cached_property
    def seconds(self) -> float:
        return self.time.total_seconds()

    def __lt__(self, other: EditPoint) -> bool:
        return self.seconds < other.seconds
