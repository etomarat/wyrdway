from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *


class _BaseProbe:
    def __init__(self, name: str) -> None:
        self.name = name

    def info(self) -> str:
        return "base:" + self.name


class _ChildProbe(_BaseProbe):
    def __init__(self, name: str, level: int) -> None:
        super().__init__(name)
        self.level = level

    def info(self) -> str:
        return "child:" + self.name + ":" + str(self.level)


_probe: _ChildProbe = _ChildProbe("ok", 2)


def class_probe_get_lines() -> list[str]:
    class_name = type(_probe).__name__
    return [
        "class=" + class_name,
        "info=" + _probe.info(),
    ]
