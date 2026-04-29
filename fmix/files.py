from __future__ import annotations

from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field, FilePath, model_validator


class Files(BaseModel, frozen=True):
    inputs: dict[str, FilePath] = Field(default_factory=dict)
    output: Path | None = None
    overwrite: bool = True

    @model_validator(mode='after')
    def check_overwrite(self) -> Self:
        if self.output and self.output.exists():
            if not self.overwrite:
                raise FileExistsError(f'{self.output=} overwrites an existing file')
            if any(self.output.samefile(i) for i in self.inputs.values()):
                raise FileExistsError(f'{self.output=} overwrites one of its inputs')
        return self
