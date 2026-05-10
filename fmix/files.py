from __future__ import annotations

from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, Field, FilePath, model_validator

from . import tyro_arg


class Files(BaseModel, frozen=True):
    # A map from mix names to file names
    inputs: Annotated[dict[str, FilePath], tyro_arg('-i')] = Field(default_factory=dict)

    # A single output file, which must be distinct from any input file
    output: Annotated[Path | None, tyro_arg('-o')] = None

    # Can the output file overwrite an existing file?
    overwrite: Annotated[bool, tyro_arg('-w')] = False

    @model_validator(mode='after')
    def check_overwrite(self) -> Self:
        if self.output and self.output.exists():
            if not self.overwrite:
                raise FileExistsError(f'{self.output=} overwrites an existing file')
            if any(self.output.samefile(i) for i in self.inputs.values()):
                raise FileExistsError(f'{self.output=} overwrites one of its inputs')
        return self
