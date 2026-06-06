import sys

from fmix.read_tyro import read_tyro

from .fmix import FMix


def main():
    fmix = read_tyro(cls=FMix, prog='fmix')
    sys.exit(fmix())


if __name__ == '__main__':
    main()
