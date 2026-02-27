from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controls.prompts import (
        filter_prompt_glyphs,
        format_prompt,
        prompt_glyphs_for_action
    )
    from ..controls.actions import ActionId

    from typing import Protocol

    from ..controls.modes import InputDeviceModeId, PromptGlyphDetailId

    class PromptState(Protocol):
        @property
        def input_device_mode(self) -> InputDeviceModeId: ...

        @property
        def prompt_glyph_detail(self) -> PromptGlyphDetailId: ...

        @property
        def prompt_show_shoulders(self) -> bool: ...
else:
    PromptState = object
    ActionId = int


def ui_prompt_for_action(state: PromptState, action: ActionId, show_shoulders: bool | None = None) -> str:
    glyphs = prompt_glyphs_for_action(action, state.input_device_mode)
    if show_shoulders is None:
        show_shoulders = bool(state.prompt_show_shoulders)
    if not show_shoulders:
        # PocketPy keyword argument handling is not always consistent; pass
        # positionally.
        glyphs = filter_prompt_glyphs(glyphs, False)
    return format_prompt(glyphs, state.prompt_glyph_detail)
