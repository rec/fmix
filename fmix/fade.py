from __future__ import annotations

import dataclasses as dc

from fmix.curve import Curve
from fmix.excepter import Excepter


@dc.dataclass(frozen=True)
class Fade:
    curve: Curve = Curve.tri
    duration: float = 1.0  # Negative means a gap? or is illegal?

    def check(self) -> None:
        with Excepter('Fade') as ex:
            if self.curve == 'linear':
                self.__dict__['curve'] = Curve.tri
            else:
                ex.call(Curve, self.curve)
