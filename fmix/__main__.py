from . import fmix


def main():
    f = fmix.FMix.from_tyro()
    assert f or not f


if __name__ == '__main__':
    main()
