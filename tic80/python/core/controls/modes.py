from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    InputDeviceModeId: TypeAlias = Literal[0, 1, 2]
    PromptGlyphDetailId: TypeAlias = Literal[0, 1]
else:
    InputDeviceModeId = int
    PromptGlyphDetailId = int


class InputDeviceMode:
    """Какой набор подсказок показываем в UI.

    Важно: это не "детекция устройства". В текущем билде триггеры/бамперы могут
    быть замаплены на те же сигналы, что и face buttons, поэтому различить их по
    вводу нельзя. Это чисто настройка отображения.
    """

    GAMEPAD: InputDeviceModeId = 0
    KEYBOARD: InputDeviceModeId = 1
    BOTH: InputDeviceModeId = 2


class PromptGlyphDetail:
    """Насколько подробные подсказки показываем для одного действия."""

    ALL: PromptGlyphDetailId = 0
    PRIMARY_ONLY: PromptGlyphDetailId = 1
