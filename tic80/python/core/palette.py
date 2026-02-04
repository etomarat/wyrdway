from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    # Строгий тип для цветов TIC-80 (0..15) для редактора/линтера.
    ColorId: TypeAlias = Literal[
        0, 1, 2, 3, 4, 5, 6, 7,
        8, 9, 10, 11, 12, 13, 14, 15
    ]
else:
    # В рантайме (PocketPy) это остаётся обычным int.
    ColorId = int


class Color:
    """Имена для индексов дефолтной палитры TIC-80 (SWEETIE-16).

    Источник:
    - `docs/30_style/0_palette_sweetie16.md`
    """

    BLACK: ColorId = 0
    PURPLE: ColorId = 1
    RED: ColorId = 2
    ORANGE: ColorId = 3
    YELLOW: ColorId = 4
    LIGHT_GREEN: ColorId = 5
    GREEN: ColorId = 6
    DARK_GREEN: ColorId = 7
    DARK_BLUE: ColorId = 8
    BLUE: ColorId = 9
    LIGHT_BLUE: ColorId = 10
    CYAN: ColorId = 11
    WHITE: ColorId = 12
    LIGHT_GREY: ColorId = 13
    GREY: ColorId = 14
    DARK_GREY: ColorId = 15
