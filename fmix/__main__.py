import json
import tomllib
from functools import partial
from pathlib import Path
from typing import Any, TypeIs

import tyro

from .fmix import FMix


def is_str_dict(x: Any) -> TypeIs[dict[str, Any]]:
    return isinstance(x, dict) and all(isinstance(k, str) for k in x.keys())


def read_file(path: Path) -> dict[str, Any]:
    data = path.read_text()
    match path.suffix:
        case '.toml':
            result = tomllib.loads(data)
        case '.json':
            result = json.loads(data)
        case _:
            raise ValueError(f'Do not understand file {path}')
    if not is_str_dict(result):
        raise ValueError(f'File {path} does not contain a string dictionary')
    return result


def read_fmix(path: Path) -> FMix:
    return FMix(**read_file(path))


def main():
    cli = partial(tyro.cli, FMix, prog='fmix')
    f = cli()
    return cli(default=read_fmix(f.config_file)) if f.config_file else f


if __name__ == '__main__':
    main()
