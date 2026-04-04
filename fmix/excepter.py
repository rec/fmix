from contextlib import contextmanager
from typing import Any


class Excepter:
    def __init__(self, name: str, *exceptions: Exception) -> None:
        self.name = name
        self.exceptions = list(exceptions)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex, tb):
        if ex:
            self(ex)
        if self.exceptions:
            raise ExceptionGroup(self.name, self.exceptions)

    def call(self, callable, *args: Any, **kwargs: Any) -> Any:
        with self.catch():
            return callable(*args, **kwargs)

    @contextmanager
    def catch(self):
        try:
            yield
        except Exception as e:
            self(e)

    def make(self, cls: type, *args: Any, **kwargs: Any) -> Any:
        c = self.call(cls, *args, **kwargs)
        if (check := getattr(c, 'check', None)) is not None:
            self.call(check)
        return c

    def __call__(self, *exs: str | Exception) -> None:
        for e in exs:
            if isinstance(e, ExceptionGroup):
                self.exceptions.extend(e.exceptions)
            elif isinstance(e, Exception):
                self.exceptions.append(e)
            elif isinstance(e, str):
                self.exceptions.append(ValueError(e))
            else:
                assert isinstance(e, str), (e, type(e))
