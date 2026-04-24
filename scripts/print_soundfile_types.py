import json

import soundfile as sf


def list_types() -> None:
    d = {f: ' '.join(sf.available_subtypes(f)) for f in sf.available_formats()}
    print(json.dumps(d, indent=4))


if __name__ == '__main__':
    list_types()
