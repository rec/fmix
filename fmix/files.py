from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, FilePath

from . import tyro_arg


class Files(BaseModel, frozen=True):
    # A map from mix names to file names
    inputs: Annotated[dict[str, FilePath], tyro_arg('-i')] = Field(default_factory=dict)

    # A single output file, which must be distinct from any input file
    output: Annotated[Path | None, tyro_arg('-o')] = None

    # Can the output file overwrite an existing file?
    overwrite: Annotated[bool, tyro_arg('-w')] = False

    def check_overwrite(self) -> None:
        if self.output and self.output.exists():
            if not self.overwrite:
                print(self.model_dump(), file=sys.stderr)
                raise FileExistsError(f'{self.output=} overwrites an existing file')
            if any(self.output.samefile(i) for i in self.inputs.values()):
                raise FileExistsError(f'{self.output=} overwrites one of its inputs')
