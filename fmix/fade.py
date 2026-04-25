from __future__ import annotations

import dataclasses as dc

import ffmpeg as ff
from ffmpeg.nodes import InputNode

from fmix.curve import Curve
from fmix.excepter import Excepter


@dc.dataclass(frozen=True)
class Fade:
    curve: Curve = Curve.tri
    duration: float = 1.0  # Negative means a gap? or is illegal?

    def crossfade(self, a: InputNode, b: InputNode) -> InputNode:
        c, d = self.curve, self.duration
        return ff.filter((a, b), 'acrossfade', curve1=c, curve2=c, duration=d)

    def fade(self, a: InputNode, type_: str) -> InputNode:
        return ff.filter(a, 'afade', type=type_, duration=self.duration)

    def check(self) -> None:
        with Excepter('Fade') as ex:
            if self.curve == 'linear':
                self.__dict__['curve'] = Curve.tri
            else:
                ex.call(Curve, self.curve)
