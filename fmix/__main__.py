from pathlib import Path

import tyro

from . import fmix


class FMix(fmix.FMix, frozen=True):
    config_file: Path | None = None


def main():
    from .audio import Audio

    args = tyro.cli(Audio)
    print(args)


if __name__ == '__main__':
    main()
