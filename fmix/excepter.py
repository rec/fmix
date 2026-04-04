from contextlib import contextmanager


class Excepter:
    def __init__(self, name: str, *exceptions: Exception) -> None:
        self.name = name
        self.exceptions = list(exceptions)

    def __enter__(self):
        pass

    def __exit__(self, e, *a):
        if e:
            self(e)
        if self.exceptions:
            raise ExceptionGroup(self.name, self.exceptions)

    @contextmanager
    def catch(self):
        try:
            yield
        except Exception as e:
            self(e)

    def __call__(self, *exs: str | Exception) -> None:
        for e in exs:
            if isinstance(e, ExceptionGroup):
                self.exceptions.extend(e.exceptions)
            else:
                if isinstance(e, str):
                    e = ValueError(e)
                self.exceptions.append(e)
