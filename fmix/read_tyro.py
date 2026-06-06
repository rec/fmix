import json
import sys
import tomllib
from functools import partial
from pathlib import Path
from typing import Any, TypeIs

import tyro
from pydantic import ValidationError


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


def read_tyro(cls: type, prog: str):
    cli = partial(tyro.cli, cls, prog=prog)
    try:
        if (f := cli()).config_file:
            f = cli(default=cls(**read_file(f.config_file)))
        result = f()
    except (ValidationError, FileExistsError) as e:
        if getattr(locals().get('f'), 'verbose', False):
            raise
        result = str(e)
    sys.exit(result)
