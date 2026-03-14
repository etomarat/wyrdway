from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, cls, line, pix, print, rect

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action, ActionId
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_right_x, text_width
    from ..core.ui.footer_slots import (
        ui_footer_slot_indices
    )
    from ..core.ui.modal_spec import (
        UiModalSpec,
        ui_modal_footer_slots,
        ui_modal_keyboard_active,
        ui_modal_nav_enabled
    )
    from ..core.ui.input_layer import UiInputLayer
    from ..core.ui.overlay_layout import (
        OverlayLayout,
        ui_overlay_footer_positions,
        ui_overlay_layout_int,
        ui_overlay_layout_slot_count
    )
    from ..core.ui.overlay_screen import ui_overlay_screen_draw
    from ..core.version import game_version_label
    from .main_menu_overlays import (
        MAIN_MENU_OVERLAY_CONTROLS,
        MAIN_MENU_OVERLAY_CREDITS,
        MAIN_MENU_OVERLAY_NEW_GAME_CONFIRM,
        MAIN_MENU_OVERLAY_NEW_GAME_SEED,
        MAIN_MENU_OVERLAY_NEW_GAME_SETUP,
        MAIN_MENU_OVERLAY_NONE,
        MainMenuOverlayDef,
        MainMenuNewGameFlow,
        MainMenuOverlayFlow,
        build_main_menu_overlay_defs,
        main_menu_overlay_default_layout
    )
    from .drive.pursuer_text_bank import PursuerTextBank
    from .main_menu_backdrop import MainMenuBackdrop, make_main_menu_backdrop
else:
    OverlayLayout = dict

class MainMenuScene:
    SCENE_ID = SceneId.MAIN_MENU
    _LEFT_X = 4
    _LEFT_Y = 20
    _LEFT_W = 88
    _LEFT_H = 114
    _RIGHT_X = 96
    _RIGHT_Y = 20
    _RIGHT_W = 140
    _RIGHT_H = 114
    _LEFT_HEADER_TEXT = "MAIN MENU"

    _ITEM_CONTINUE = 0
    _ITEM_NEW_GAME = 1
    _ITEM_CONTROLS = 2
    _ITEM_CREDITS = 3

    _MENU_ITEMS: list[tuple[int, str]] = [
        (_ITEM_CONTINUE, "CONTINUE"),
        (_ITEM_NEW_GAME, "NEW GAME"),
        (_ITEM_CONTROLS, "OPTIONS"),
        (_ITEM_CREDITS, "CREDITS")
    ]

    _OVERLAY_NONE = MAIN_MENU_OVERLAY_NONE
    _OVERLAY_CONTROLS = MAIN_MENU_OVERLAY_CONTROLS
    _OVERLAY_CREDITS = MAIN_MENU_OVERLAY_CREDITS
    _OVERLAY_NEW_GAME_CONFIRM = MAIN_MENU_OVERLAY_NEW_GAME_CONFIRM
    _OVERLAY_NEW_GAME_SETUP = MAIN_MENU_OVERLAY_NEW_GAME_SETUP
    _OVERLAY_NEW_GAME_SEED = MAIN_MENU_OVERLAY_NEW_GAME_SEED
    _OVERLAY_BODY_X_PAD = 8
    _OVERLAY_BODY_LINE_STEP = 8
    _WATCH_PULSE_SECONDS = 4.8
    _WATCH_GLITCH_SECONDS = 0.18
    _WATCH_ERROR_HOLD_SECONDS = 0.18
    _WATCH_REC_BLINK_HZ = 2.0
    _WATCH_STATIC_DOTS = 0
    _WATCH_STATIC_DOTS_PULSE = 4

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._menu_ui = UiInputLayer()
        self._overlay_ui = UiInputLayer()
        self._selected = 0
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_left_down = False
        self._mouse_left_pressed = False
        self._mouse_left_released = False
        self._mouse_right_down = False
        self._mouse_right_pressed = False
        self._mouse_right_released = False
        self._mouse_scroll_y = 0
        self._menu_mouse_hover_index = -1
        self._menu_mouse_down_index = -1
        self._backdrop: MainMenuBackdrop = make_main_menu_backdrop()
        self._watch_text_bank = PursuerTextBank()
        self._watch_seed = 0x13579BDF
        self._watch_event_t = 0.0
        self._watch_glitch_t = 0.0
        self._watch_error_t = 0.0
        self._watch_error_text = ""
        self._watch_rec_t = 0.0
        self._new_game_flow = MainMenuNewGameFlow(
            self._state.input_device_mode,
            self._state.drive_preset_id
        )
        self._overlay_defs: dict[int, MainMenuOverlayDef] = (
            build_main_menu_overlay_defs(self._state, self._new_game_flow)
        )
        self._overlay_specs: dict[int, UiModalSpec] = {}
        self._overlay_flows: dict[int, MainMenuOverlayFlow] = {}
        for overlay_id in self._overlay_defs:
            overlay_def = self._overlay_defs[overlay_id]
            self._overlay_specs[int(overlay_id)] = overlay_def.spec
            self._overlay_flows[int(overlay_id)] = overlay_def.flow
        self._overlay_layout_default = main_menu_overlay_default_layout()

    def enter(self, params: SceneEnterParams = None) -> None:
        self._selected = 0
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._menu_mouse_hover_index = -1
        self._menu_mouse_down_index = -1
        self._menu_ui.reset_footer()
        self._overlay_ui.reset_footer()
        self._apply_input_context(True)
        self._backdrop.enter()
        self._watch_seed = (0x13579BDF ^ (
            (int(self._state.run_index) + 1) * 97)) & 0xFFFFFFFF
        if self._watch_seed == 0:
            self._watch_seed = 1
        self._watch_event_t = 0.0
        self._watch_glitch_t = 0.0
        self._watch_error_t = 0.0
        self._watch_error_text = ""
        self._watch_rec_t = 0.0

    def update(self, dt: float) -> None:
        self._poll_mouse_state()
        self._backdrop.update(dt)
        self._update_entity_watch(dt)
        if self._overlay != self._OVERLAY_NONE:
            self._update_overlay_input()
            return

        nav_up_released, nav_down_released = self._poll_menu_nav_release_events()
        if nav_up_released:
            self._selected -= 1
        elif nav_down_released:
            self._selected += 1

        item_count = len(self._MENU_ITEMS)
        if item_count > 0:
            while self._selected < 0:
                self._selected += item_count
            while self._selected >= item_count:
                self._selected -= item_count

        self._menu_mouse_hover_index = self._menu_item_at(
            self._mouse_x,
            self._mouse_y
        )
        if self._menu_mouse_hover_index >= 0:
            self._selected = self._menu_mouse_hover_index

        mouse_confirm_released = self._poll_menu_mouse_confirm_release()
        keyboard_confirm_released = self._poll_menu_confirm_release()
        if mouse_confirm_released or keyboard_confirm_released:
            self._activate_selected_item()

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_title()
        self._draw_gameplay_panel()
        self._draw_left_column()
        self._draw_footer()
        self._draw_overlay()

    def exit(self) -> None:
        pass

    def _has_continue(self) -> bool:
        return self._state.profile_loaded

    def _update_overlay_input(self) -> None:
        nav_up_released, nav_down_released, nav_left_released, nav_right_released, confirm_released, cancel_released = self._poll_overlay_release_events()
        secondary_released = self._overlay_ui.poll_action(
            self._state.controls, Action.SECONDARY
        )
        mouse_nav_released, mouse_confirm_released, mouse_cancel_released = self._poll_overlay_footer_mouse_release()
        if (
            secondary_released
            or mouse_nav_released
            or mouse_confirm_released
            or mouse_cancel_released
            or confirm_released
            or cancel_released
        ):
            self._state.vibe_ui_button()
        if mouse_confirm_released:
            confirm_released = True
        if mouse_cancel_released:
            cancel_released = True
        flow = self._overlay_flow(self._overlay)
        if flow is not None:
            flow.update(
                self,
                nav_up_released,
                nav_down_released,
                nav_left_released,
                nav_right_released,
                confirm_released,
                cancel_released,
                secondary_released,
                mouse_nav_released
            )
            return

        if mouse_nav_released:
            nav_down_released = True
        body_lines = self._overlay_body_lines_for(self._overlay)
        self._clamp_overlay_scroll(body_lines)
        if nav_up_released:
            self._overlay_scroll -= 1
            self._clamp_overlay_scroll(body_lines)
        elif nav_down_released:
            self._overlay_scroll += 1
            self._clamp_overlay_scroll(body_lines)

        if cancel_released or confirm_released:
            self._close_overlay()

    def _start_new_campaign_from_setup(self) -> None:
        self._new_game_flow.start_campaign(self._state)
        self._close_overlay()
        self._nav.go(SceneId.GARAGE)

    def _open_new_game_seed_overlay(self) -> None:
        self._open_overlay(self._OVERLAY_NEW_GAME_SEED)

    def _activate_selected_item(self) -> None:
        item_id, _ = self._MENU_ITEMS[self._selected]
        if item_id == self._ITEM_CONTINUE:
            if not self._has_continue():
                return
            self._state.load_profile()
            if not self._has_continue():
                return
            self._state.vibe_ui_button()
            self._nav.go(SceneId.GARAGE)
            return
        if item_id == self._ITEM_NEW_GAME:
            self._state.vibe_ui_button()
            if self._has_continue():
                self._open_overlay(self._OVERLAY_NEW_GAME_CONFIRM)
                return
            self._open_overlay(self._OVERLAY_NEW_GAME_SETUP)
            return
        if item_id == self._ITEM_CONTROLS:
            self._state.vibe_ui_button()
            self._open_overlay(self._OVERLAY_CONTROLS)
            return
        if item_id == self._ITEM_CREDITS:
            self._state.vibe_ui_button()
            self._open_overlay(self._OVERLAY_CREDITS)
            return

    def _open_overlay(self, overlay_id: int) -> None:
        prev_overlay = self._overlay
        self._overlay = int(overlay_id)
        self._overlay_scroll = 0
        self._menu_mouse_down_index = -1
        self._overlay_ui.reset_footer()
        flow = self._overlay_flow(self._overlay)
        if flow is not None:
            flow.on_open(self, prev_overlay)
        self._apply_input_context(True)

    def _close_overlay(self) -> None:
        flow = self._overlay_flow(self._overlay)
        if flow is not None:
            flow.on_close(self)
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._overlay_ui.reset_footer()
        self._apply_input_context(True)

    def _poll_mouse_state(self) -> None:
        ui = self._menu_ui
        if self._overlay != self._OVERLAY_NONE:
            ui = self._overlay_ui
        ui.poll_mouse()
        self._mouse_left_pressed = ui.mouse.left_pressed
        self._mouse_left_released = ui.mouse.left_released
        self._mouse_left_down = ui.mouse.left_down
        self._mouse_right_pressed = ui.mouse.right_pressed
        self._mouse_right_released = ui.mouse.right_released
        self._mouse_right_down = ui.mouse.right_down
        self._mouse_x = ui.mouse.x
        self._mouse_y = ui.mouse.y
        self._mouse_scroll_y = ui.mouse.scroll_y

    def _poll_menu_confirm_release(self) -> bool:
        return self._menu_ui.poll_action(self._state.controls, Action.CONFIRM)

    def _poll_menu_nav_release_events(self) -> tuple[bool, bool]:
        return (
            self._menu_ui.poll_action(self._state.controls, Action.NAV_UP),
            self._menu_ui.poll_action(self._state.controls, Action.NAV_DOWN)
        )

    def _poll_menu_mouse_confirm_release(self) -> bool:
        hover_idx = self._menu_mouse_hover_index
        if self._mouse_left_pressed:
            self._menu_mouse_down_index = hover_idx
        if not self._mouse_left_down and not self._mouse_left_released:
            self._menu_mouse_down_index = -1
        if not self._mouse_left_released:
            return False
        activated = (
            self._menu_mouse_down_index >= 0
            and self._menu_mouse_down_index == hover_idx
        )
        self._menu_mouse_down_index = -1
        return activated

    def _poll_overlay_footer_mouse_release(self) -> tuple[bool, bool, bool]:
        if self._overlay == self._OVERLAY_NONE:
            self._overlay_ui.reset_footer()
            return False, False, False
        spec = self._overlay_spec()
        if spec is None:
            self._overlay_ui.reset_footer()
            return False, False, False
        footer = spec.footer
        layout = self._overlay_layout()
        has_scroll = self._overlay_scrollable(self._overlay, layout)
        nav_enabled = ui_modal_nav_enabled(footer.nav_mode, has_scroll)
        slot_count = ui_overlay_layout_slot_count(layout)
        slots = ui_modal_footer_slots(
            layout,
            slot_count,
            self._state,
            footer,
            nav_enabled
        )
        released_slot = self._overlay_ui.poll_footer_release(layout, slots)
        slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(
            layout, slot_count)
        return (
            nav_enabled and released_slot == slot_nav,
            released_slot == slot_confirm,
            released_slot == slot_cancel
        )

    def _apply_input_context(self, swallow_held: bool) -> None:
        actions: list[ActionId] = [
            Action.NAV_UP,
            Action.NAV_DOWN,
            Action.CONFIRM
        ]
        if self._overlay != self._OVERLAY_NONE:
            self._overlay_ui.activate(
                self._state.controls,
                [
                    Action.NAV_UP,
                    Action.NAV_DOWN,
                    Action.NAV_LEFT,
                    Action.NAV_RIGHT,
                    Action.CONFIRM,
                    Action.CANCEL,
                    Action.SECONDARY
                ],
                swallow_held
            )
            return
        self._menu_ui.activate(
            self._state.controls,
            actions,
            swallow_held
        )

    def _poll_overlay_release_events(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return (
            self._overlay_ui.poll_action(self._state.controls, Action.NAV_UP),
            self._overlay_ui.poll_action(self._state.controls, Action.NAV_DOWN),
            self._overlay_ui.poll_action(self._state.controls, Action.NAV_LEFT),
            self._overlay_ui.poll_action(self._state.controls, Action.NAV_RIGHT),
            self._overlay_ui.poll_action(self._state.controls, Action.CONFIRM),
            self._overlay_ui.poll_action(self._state.controls, Action.CANCEL)
        )

    def _overlay_nav_any_down(self) -> bool:
        return (
            self._overlay_ui.down(self._state.controls, Action.NAV_UP)
            or self._overlay_ui.down(self._state.controls, Action.NAV_DOWN)
            or self._overlay_ui.down(self._state.controls, Action.NAV_LEFT)
            or self._overlay_ui.down(self._state.controls, Action.NAV_RIGHT)
        )

    def _overlay_down(self, action: ActionId) -> bool:
        return self._overlay_ui.down(self._state.controls, action)

    def _menu_down(self, action: ActionId) -> bool:
        return self._menu_ui.down(self._state.controls, action)

    def _draw_title(self) -> None:
        rect(0, 0, 240, 18, Color.BLACK)
        line(0, 17, 239, 17, Color.GREY)
        title = "W Y R D W A Y"
        tx = 6
        ty = 3
        print(title, tx + 1, ty + 1, Color.RED, True, 2)
        print(title, tx, ty, Color.YELLOW, True, 2)
        ver = game_version_label()
        ver_x = tx + text_width(title, 12) + 6
        ver_y = ty + 6
        print(ver, ver_x, ver_y, Color.GREY, fixed=True, alt=True)

    def _draw_gameplay_panel(self) -> None:
        x = self._RIGHT_X
        y = self._RIGHT_Y
        w = self._RIGHT_W
        h = self._RIGHT_H
        rect(x - 1, y - 1, w + 2, h + 2, Color.GREY)
        rect(x, y, w, h, Color.BLACK)
        self._backdrop.draw(x, y, w, h)
        self._draw_entity_watch_static_noise(x, y, w, h)
        self._draw_entity_watch_glitch(x, y, w, h)
        self._draw_entity_watch_header(x, y)
        self._draw_entity_watch_error(x, y, w, h)

    def _draw_left_column(self) -> None:
        x = self._LEFT_X
        y = self._LEFT_Y
        w = self._LEFT_W
        h = self._LEFT_H
        rect(x - 1, y - 1, w + 2, h + 2, Color.GREY)
        rect(x, y, w, h, Color.BLACK)
        line(x, y + 11, x + w - 1, y + 11, Color.DARK_GREY)
        print(self._LEFT_HEADER_TEXT, x + 3, y + 3, Color.LIGHT_GREY)
        self._draw_menu_items(x + 4, y + 16)
        self._draw_left_save_info(x, y, w, h)

    def _draw_menu_items(self, x: int, y: int) -> None:
        i = 0
        while i < len(self._MENU_ITEMS):
            item_id, label = self._MENU_ITEMS[i]
            enabled = True
            if item_id == self._ITEM_CONTINUE:
                enabled = self._has_continue()
            selected = i == self._selected
            color = Color.WHITE
            if not enabled:
                color = Color.GREY
            if selected and enabled:
                color = Color.YELLOW
            active = self._menu_item_active(i, enabled, selected)
            if active:
                rect(self._LEFT_X + 2, y - 1,
                     self._LEFT_W - 4, 8, Color.DARK_GREY)
                if enabled:
                    color = Color.WHITE
            marker = "  "
            if selected:
                marker = "> "
            print(marker + label, x, y, color)
            y += 10
            i += 1

    def _menu_item_active(self, index: int, enabled: bool, selected: bool) -> bool:
        # UI rule: when a modal/overlay is open, background UI must not react.
        # Keep this behavior when moving modals to a shared UI layer.
        if self._overlay != self._OVERLAY_NONE:
            return False
        if not enabled:
            return False
        keyboard_active = (
            selected
            and self._overlay == self._OVERLAY_NONE
            and self._menu_down(Action.CONFIRM)
        )
        mouse_active = (
            self._mouse_left_down
            and self._menu_mouse_down_index == index
            and self._menu_mouse_hover_index == index
        )
        return keyboard_active or mouse_active

    def _menu_item_at(self, mx: int, my: int) -> int:
        row_x = self._LEFT_X + 2
        row_w = self._LEFT_W - 4
        if mx < row_x or mx >= row_x + row_w:
            return -1
        y0 = self._LEFT_Y + 16
        i = 0
        while i < len(self._MENU_ITEMS):
            row_y = y0 + i * 10
            if my >= row_y - 1 and my < row_y + 7:
                return i
            i += 1
        return -1

    def _draw_left_save_info(self, x: int, y: int, w: int, h: int) -> None:
        if not self._has_continue():
            return
        if self._overlay != self._OVERLAY_NONE:
            return
        selected_id, _ = self._MENU_ITEMS[self._selected]
        if selected_id != self._ITEM_CONTINUE:
            return

        profile = self._state.profile
        row_step = 8
        seed_row_y = y + h - 9
        row_y = seed_row_y - row_step * 4
        split_y = row_y - 14
        line(x, split_y, x + w - 1, split_y, Color.DARK_GREY)
        print("ON CONTINUE", x + 3, split_y + 4, Color.LIGHT_GREY)
        self._draw_kv_row(x, w, row_y, "HP", str(
            self._to_ui_int(profile.garage_hp)), Color.WHITE, Color.WHITE)
        self._draw_kv_row(x, w, row_y + row_step, "FUEL",
                          str(self._to_ui_int(profile.garage_fuel)), Color.WHITE, Color.WHITE)
        self._draw_kv_row(x, w, row_y + row_step * 2, "SCRAP",
                          str(profile.scrap), Color.LIGHT_GREY, Color.LIGHT_GREY)
        self._draw_kv_row(x, w, row_y + row_step * 3, "RUNS",
                          str(self._state.run_index), Color.GREY, Color.GREY)
        self._draw_kv_row(x, w, row_y + row_step * 4, "SEED",
                          self._state.campaign_seed_text, Color.GREY, Color.GREY)

    @staticmethod
    def _to_ui_int(value: float) -> int:
        if value >= 0.0:
            return int(value + 0.5)
        return int(value - 0.5)

    @staticmethod
    def _draw_kv_row(
        x: int,
        w: int,
        y: int,
        label: str,
        value: str,
        label_color: int,
        value_color: int
    ) -> None:
        print(label, x + 3, y, label_color)
        value_x = text_right_x(value, x + w - 3, 6, x + 3)
        print(value, value_x, y, value_color, fixed=True)

    def _draw_footer(self) -> None:
        return

    def _update_entity_watch(self, dt: float) -> None:
        if dt < 0.0:
            dt = 0.0
        if self._watch_glitch_t > 0.0:
            self._watch_glitch_t -= dt
            if self._watch_glitch_t < 0.0:
                self._watch_glitch_t = 0.0
                self._watch_error_text = ""
                self._watch_error_t = 0.0
        if self._watch_error_t > 0.0:
            self._watch_error_t -= dt
            if self._watch_error_t <= 0.0:
                self._watch_error_t = 0.0
                self._watch_error_text = ""
        self._watch_rec_t += dt

        self._watch_event_t += dt
        if self._watch_event_t < self._WATCH_PULSE_SECONDS:
            return
        while self._watch_event_t >= self._WATCH_PULSE_SECONDS:
            self._watch_event_t -= self._WATCH_PULSE_SECONDS
        self._trigger_entity_watch_glitch()

    def _trigger_entity_watch_glitch(self) -> None:
        seed = self._next_watch_seed()
        txt = self._watch_text_bank.entity_error_text(seed)
        if txt == "":
            txt = "NULL PTR"
        self._watch_error_text = txt
        self._watch_glitch_t = self._WATCH_GLITCH_SECONDS
        self._watch_error_t = self._WATCH_ERROR_HOLD_SECONDS

    def _draw_entity_watch_header(self, x: int, y: int) -> None:
        rect(x + 2, y + 2, 84, 8, Color.BLACK)
        blink_on = (int(self._watch_rec_t * self._WATCH_REC_BLINK_HZ) & 1) == 0
        if self._watch_glitch_t > 0.0:
            blink_on = True
        if blink_on:
            circ(x + 6, y + 5, 2, Color.RED)
        print("ENTITY WATCH", x + 12, y + 3, Color.LIGHT_GREY)

    def _draw_entity_watch_error(self, x: int, y: int, w: int, h: int) -> None:
        if self._watch_glitch_t <= 0.0:
            return
        txt = self._watch_error_text
        if txt == "":
            return
        tx = text_right_x(txt, x + w - 4, 6, x + 4)
        ty = y + h - 9
        tw = len(txt) * 6 + 2
        rect(tx - 1, ty - 1, tw, 8, Color.BLACK)
        print(txt, tx, ty, Color.RED)

    def _draw_entity_watch_glitch(self, x: int, y: int, w: int, h: int) -> None:
        active_pulse = self._watch_glitch_t > 0.0
        line_count = 1
        if active_pulse:
            line_count = 5
        i = 0
        while i < line_count:
            s = self._next_watch_seed()
            gx = x + 3 + int(s % (w - 10))
            gy = y + 10 + int((s >> 8) % (h - 16))
            span = 6 + int((s >> 16) % 26)
            if not active_pulse:
                span = 4 + int((s >> 16) % 12)
            max_right = x + w - 3
            gx2 = gx + span
            if gx2 > max_right:
                gx2 = max_right
            color = Color.DARK_GREY
            if active_pulse and (s & 3) == 0:
                color = Color.LIGHT_GREY
            line(gx, gy, gx2, gy, color)
            i += 1
        if active_pulse:
            bseed = self._next_watch_seed()
            by = y + 12 + int((bseed >> 8) % (h - 20))
            rect(x + 2, by, w - 4, 2, Color.DARK_GREY)

    def _draw_entity_watch_static_noise(self, x: int, y: int, w: int, h: int) -> None:
        dots = self._WATCH_STATIC_DOTS
        if self._watch_glitch_t > 0.0:
            dots = self._WATCH_STATIC_DOTS_PULSE
        i = 0
        while i < dots:
            s = self._next_watch_seed()
            px = x + 2 + int(s % (w - 4))
            py = y + 10 + int((s >> 8) % (h - 12))
            c = Color.DARK_GREY
            if (s & 7) == 0:
                c = Color.GREY
            if self._watch_glitch_t > 0.0 and (s & 15) == 0:
                c = Color.LIGHT_GREY
            pix(px, py, c)
            i += 1

    def _next_watch_seed(self) -> int:
        self._watch_seed = (self._watch_seed * 1664525 +
                            1013904223) & 0xFFFFFFFF
        if self._watch_seed == 0:
            self._watch_seed = 1
        return int(self._watch_seed)

    def _draw_overlay(self) -> None:
        if self._overlay == self._OVERLAY_NONE:
            return
        flow = self._overlay_flow(self._overlay)
        if flow is None:
            return
        flow.draw(
            self,
            self._OVERLAY_BODY_X_PAD,
            self._OVERLAY_BODY_LINE_STEP
        )

    def _draw_overlay_box(
        self,
        title: str,
        lines: list[str],
        line_colors: list[int] | None = None
    ) -> None:
        layout = self._overlay_layout()
        slots, keyboard_active, button_bg_color = self._overlay_footer_state(
            layout)
        x, _y, w, _h, body_top, _footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            self._overlay_ui.runtime,
            layout,
            title,
            [],
            slots,
            keyboard_active,
            body_line_step=self._OVERLAY_BODY_LINE_STEP,
            button_bg_color=button_bg_color
        )
        wrapped, wrapped_colors = self._overlay_wrap_lines_with_colors(
            lines,
            line_colors,
            layout
        )
        self._clamp_overlay_scroll(lines, layout)
        visible_lines = self._overlay_visible_lines(layout)
        max_scroll = self._overlay_max_scroll(lines, layout)
        body_x = x + self._OVERLAY_BODY_X_PAD
        draw_y = body_top
        i = 0
        while i < visible_lines:
            src_i = self._overlay_scroll + i
            if src_i >= len(wrapped):
                break
            print(wrapped[src_i], body_x, draw_y, wrapped_colors[src_i])
            draw_y += self._OVERLAY_BODY_LINE_STEP
            i += 1
        if max_scroll > 0:
            up_color = Color.DARK_GREY
            down_color = Color.DARK_GREY
            if self._overlay_scroll > 0:
                up_color = Color.LIGHT_GREY
            if self._overlay_scroll < max_scroll:
                down_color = Color.LIGHT_GREY
            print("^", x + w - 9, body_top, up_color)
            print("v", x + w - 9, body_top +
                  (visible_lines - 1) * self._OVERLAY_BODY_LINE_STEP, down_color)

    def _overlay_body_lines_for(self, overlay_id: int) -> list[str]:
        flow = self._overlay_flow(overlay_id)
        if flow is not None:
            return flow.body_lines()
        return []

    def _overlay_flow(self, overlay_id: int) -> MainMenuOverlayFlow | None:
        return self._overlay_flows.get(int(overlay_id))

    def _overlay_spec(self, overlay_id: int | None = None) -> UiModalSpec | None:
        target = self._overlay
        if overlay_id is not None:
            target = int(overlay_id)
        return self._overlay_specs.get(int(target))

    def _overlay_title(self, fallback: str) -> str:
        spec = self._overlay_spec()
        if spec is None:
            return fallback
        return spec.title

    def _overlay_layout(self) -> OverlayLayout:
        spec = self._overlay_spec()
        if spec is None:
            return self._overlay_layout_default
        return spec.layout

    def _overlay_scrollable(self, overlay_id: int, layout: OverlayLayout) -> bool:
        if overlay_id == self._OVERLAY_NONE:
            return False
        lines = self._overlay_body_lines_for(overlay_id)
        return self._overlay_max_scroll(lines, layout) > 0

    def _overlay_footer_state(self, layout: OverlayLayout) -> tuple[list[str], list[bool], int]:
        button_bg_color = ui_overlay_layout_int(layout, "footer_bg_color", 0)
        slot_count = ui_overlay_layout_slot_count(layout)
        spec = self._overlay_spec()
        if spec is None:
            return [], [], button_bg_color
        footer = spec.footer
        has_scroll = self._overlay_scrollable(self._overlay, layout)
        nav_enabled = ui_modal_nav_enabled(footer.nav_mode, has_scroll)
        slots = ui_modal_footer_slots(
            layout,
            slot_count,
            self._state,
            footer,
            nav_enabled
        )
        keyboard_active = ui_modal_keyboard_active(
            layout,
            slot_count,
            self._state.controls,
            footer,
            nav_enabled,
            self._overlay_nav_any_down(),
            self._overlay_ui.context_token
        )
        return slots, keyboard_active, button_bg_color

    def _overlay_max_line_width_px(self, layout: OverlayLayout | None = None) -> int:
        if layout is None:
            layout = self._overlay_layout()
        box_w = ui_overlay_layout_int(layout, "box_w", 200)
        # Body text starts at left pad and can use almost all remaining modal width.
        line_w = box_w - self._OVERLAY_BODY_X_PAD - 2
        if line_w < 24:
            return 24
        return line_w

    def _overlay_visible_lines(self, layout: OverlayLayout | None = None) -> int:
        if layout is None:
            layout = self._overlay_layout()
        footer_line_y, _footer_text_y = ui_overlay_footer_positions(
            layout,
            104,
            108
        )
        body_top = ui_overlay_layout_int(layout, "body_top", 54)
        footer_cutoff = footer_line_y - 4
        body_h = footer_cutoff - body_top
        count = int(body_h / self._OVERLAY_BODY_LINE_STEP)
        if count < 1:
            return 1
        return count

    def _overlay_wrap_lines(
        self,
        lines: list[str],
        layout: OverlayLayout | None = None
    ) -> list[str]:
        max_px = self._overlay_max_line_width_px(layout)
        out: list[str] = []
        i = 0
        while i < len(lines):
            raw = str(lines[i])
            if raw == "":
                out.append("")
                i += 1
                continue
            words = raw.split(" ")
            line_text = ""
            wi = 0
            while wi < len(words):
                word = words[wi].strip()
                wi += 1
                if word == "":
                    continue
                if line_text == "":
                    if text_width(word) <= max_px:
                        line_text = word
                        continue
                    parts = self._overlay_wrap_long_word(word, max_px)
                    pi = 0
                    while pi < len(parts):
                        out.append(parts[pi])
                        pi += 1
                    continue
                trial = line_text + " " + word
                if text_width(trial) <= max_px:
                    line_text = trial
                    continue
                out.append(line_text)
                line_text = ""
                wi -= 1
            if line_text != "":
                out.append(line_text)
            i += 1
        return out

    def _overlay_wrap_lines_with_colors(
        self,
        lines: list[str],
        line_colors: list[int] | None,
        layout: OverlayLayout | None = None
    ) -> tuple[list[str], list[int]]:
        default_color = int(Color.LIGHT_GREY)
        wrapped_lines: list[str] = []
        wrapped_colors: list[int] = []
        max_px = self._overlay_max_line_width_px(layout)
        i = 0
        while i < len(lines):
            raw = str(lines[i])
            color = default_color
            if line_colors is not None and i < len(line_colors):
                color = int(line_colors[i])
            if raw == "":
                wrapped_lines.append("")
                wrapped_colors.append(color)
                i += 1
                continue
            words = raw.split(" ")
            line_text = ""
            wi = 0
            while wi < len(words):
                word = words[wi].strip()
                wi += 1
                if word == "":
                    continue
                if line_text == "":
                    if text_width(word) <= max_px:
                        line_text = word
                        continue
                    parts = self._overlay_wrap_long_word(word, max_px)
                    pi = 0
                    while pi < len(parts):
                        wrapped_lines.append(parts[pi])
                        wrapped_colors.append(color)
                        pi += 1
                    continue
                trial = line_text + " " + word
                if text_width(trial) <= max_px:
                    line_text = trial
                    continue
                wrapped_lines.append(line_text)
                wrapped_colors.append(color)
                line_text = ""
                wi -= 1
            if line_text != "":
                wrapped_lines.append(line_text)
                wrapped_colors.append(color)
            i += 1
        return wrapped_lines, wrapped_colors

    def _overlay_wrap_long_word(self, word: str, max_px: int) -> list[str]:
        parts: list[str] = []
        rest = str(word)
        while rest != "":
            cut = self._overlay_fit_prefix_chars(rest, max_px)
            if cut <= 0:
                cut = 1
            parts.append(rest[:cut])
            rest = rest[cut:]
        return parts

    @staticmethod
    def _overlay_fit_prefix_chars(text: str, max_px: int) -> int:
        if text == "":
            return 0
        max_w = int(max_px)
        if max_w < 1:
            max_w = 1
        i = 1
        last_fit = 0
        n = len(text)
        while i <= n:
            if text_width(text[:i]) > max_w:
                break
            last_fit = i
            i += 1
        if last_fit <= 0:
            return 1
        return int(last_fit)

    def _overlay_max_scroll(
        self,
        lines: list[str],
        layout: OverlayLayout | None = None
    ) -> int:
        wrapped = self._overlay_wrap_lines(lines, layout)
        max_scroll = len(wrapped) - self._overlay_visible_lines(layout)
        if max_scroll < 0:
            return 0
        return max_scroll

    def _clamp_overlay_scroll(
        self,
        lines: list[str],
        layout: OverlayLayout | None = None
    ) -> None:
        max_scroll = self._overlay_max_scroll(lines, layout)
        if self._overlay_scroll < 0:
            self._overlay_scroll = 0
            return
        if self._overlay_scroll > max_scroll:
            self._overlay_scroll = max_scroll

def make_main_menu_scene(nav: SceneNavigator) -> MainMenuScene:
    return MainMenuScene(nav)
