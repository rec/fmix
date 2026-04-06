from __future__ import annotations

import dataclasses as dc
import os
from functools import cached_property

from fmix.excepter import Excepter


@dc.dataclass(frozen=True)
class Files:
    inputs: dict[str, str] = dc.field(default_factory=dict)

    # The hardcoded name of the file
    output_file: str = ''

    # A root that's used with the long common suffix in the inputs
    output_root: str = ''

    overwrite: bool = False

    @cached_property
    def output(self) -> str:
        return self.output_file or self.output_root + os.path.commonprefix(
            list(self.inputs.values())
        )

    def check(self) -> None:
        with Excepter('Files') as ex:
            if bool(self.output_file) == bool(self.output_root):
                ex('Exactly one of `output_file` and  `output_root` must be given')

            non = (i for i in self.inputs.values() if not os.path.exists(i))
            ex(*(FileNotFoundError(i) for i in non))
            if os.path.exists(self.output):
                if not self.overwrite:
                    ex(FileExistsError(f'{self.output=} overwrites an existing file'))
                elif any(os.path.samefile(i, self.output) for i in self.inputs):
                    ex(FileExistsError(f'{self.output=} overwrites an input'))
