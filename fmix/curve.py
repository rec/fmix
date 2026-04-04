from enum import StrEnum, auto


class Curve(StrEnum):
    tri = auto()  # select triangular, linear slope (default)
    qsin = auto()  # select quarter of sine wave
    hsin = auto()  # select half of sine wave
    esin = auto()  # select exponential sine wave
    log = auto()  # select logarithmic
    ipar = auto()  # select inverted parabola
    qua = auto()  # select quadratic
    cub = auto()  # select cubic
    squ = auto()  # select square root
    cbr = auto()  # select cubic root
    par = auto()  # select parabola
    exp = auto()  # select exponential
    iqsin = auto()  # select inverted quarter of sine wave
    ihsin = auto()  # select inverted half of sine wave
    dese = auto()  # select double-exponential seat
    desi = auto()  # select double-exponential sigmoid
    losi = auto()  # select logistic sigmoid
    sinc = auto()  # select sine cardinal function
    isinc = auto()  # select inverted sine cardinal function
    quat = auto()  # select quartic
    quatr = auto()  # select quartic root
    qsin2 = auto()  # select squared quarter of sine wave
    hsin2 = auto()  # select squared half of sine wave
    nofade = auto()  # no fade applied
