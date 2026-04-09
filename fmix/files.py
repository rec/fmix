from __future__ import annotations

import dataclasses as dc
import os
from functools import cached_property

from fmix.excepter import Excepter


@dc.dataclass(frozen=True)
class Files:
    inputs: dict[str, str] = dc.field(default_factory=dict)
    output: str = ''
    overwrite: bool = True

    @cached_property
    def check(self) -> None:
        with Excepter('Files') as ex:
            non = (i for i in self.inputs.values() if not os.path.exists(i))
            ex(*(FileNotFoundError(i) for i in non))
            if os.path.exists(self.output):
                if not self.overwrite:
                    ex(FileExistsError(f'{self.output=} overwrites an existing file'))
                else:
                    try:
                        if any(os.path.samefile(i, self.output) for i in self.inputs):
                            msg = f'{self.output=} overwrites an input'
                            ex(FileExistsError(msg), str(self))
                    except FileNotFoundError:
                        pass
