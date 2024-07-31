import typing


class JanettoraConfigError(Exception):
    def __init__(self, msg: str, format__: typing.Optional[bool] = True):
        message = self.default_format(msg) if format__ else msg
        super().__init__(message)

    def default_format(self, setting: str):   # noqa
        return f"Config variable {setting} configured incorrectly."
