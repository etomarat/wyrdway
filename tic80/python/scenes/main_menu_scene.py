from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, cls, line, pix, print, rect

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_center_x, text_right_x, text_width
    from ..core.ui.prompts import (
        ui_prompt_for_action,
        ui_prompt_for_nav_hint,
        ui_prompt_with_text
    )
    from ..core.ui.rich_text import ui_rich_print, ui_rich_text_width
    from ..core.version import game_version_label
    from .drive.pursuer_text_bank import PursuerTextBank
    from .main_menu_backdrop import MainMenuBackdrop, make_main_menu_backdrop


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
        (_ITEM_CONTROLS, "CONTROLS"),
        (_ITEM_CREDITS, "CREDITS")
    ]

    _OVERLAY_NONE = 0
    _OVERLAY_CONTROLS = 1
    _OVERLAY_CREDITS = 2
    _OVERLAY_NEW_GAME_CONFIRM = 3
    _OVERLAY_BODY_X_PAD = 8
    _OVERLAY_BODY_LINE_STEP = 8
    _OVERLAY_LAYOUT_DEFAULT = {
        "box_x": 20,
        "box_y": 28,
        "box_w": 200,
        "box_h": 90,
        "header_text_y": 37,
        "body_top": 54,
        "footer_line_y": 104,
        "footer_text_y": 108,
        "footer_bg_color": 0,
        "slot_count": 4,
        "slot_weights": (1, 1, 1, 1),
        "slot_nav": 0,
        "slot_confirm": 2,
        "slot_cancel": 3
    }
    _OVERLAY_LAYOUTS = {
        _OVERLAY_CONTROLS: {
            "box_x": 14,
            "box_y": 28,
            "box_w": 212,
            "box_h": 90,
            "header_text_y": 37,
            "body_top": 54,
            "footer_line_y": 104,
            "footer_text_y": 108,
            "footer_bg_color": 0,
            "slot_count": 3,
            "slot_weights": (1, 1, 1),
            "slot_nav": 0,
            "slot_confirm": 1,
            "slot_cancel": 2
        },
        _OVERLAY_CREDITS: {
            "box_x": 20,
            "box_y": 28,
            "box_w": 200,
            "box_h": 90,
            "header_text_y": 37,
            "body_top": 54,
            "footer_line_y": 104,
            "footer_text_y": 108,
            "footer_bg_color": 0,
            "slot_count": 4,
            "slot_weights": (1, 1, 1, 1),
            "slot_nav": 0,
            "slot_confirm": 2,
            "slot_cancel": 3
        },
        _OVERLAY_NEW_GAME_CONFIRM: {
            "box_x": 20,
            "box_y": 28,
            "box_w": 200,
            "box_h": 90,
            "header_text_y": 37,
            "body_top": 54,
            "footer_line_y": 104,
            "footer_text_y": 108,
            "footer_bg_color": 0,
            "slot_count": 2,
            "slot_weights": (1, 1),
            "slot_nav": 0,
            "slot_confirm": 0,
            "slot_cancel": 1
        }
    }
    _OVERLAY_FOOTER_DEBUG_SLOTS = False
    _WATCH_PULSE_SECONDS = 4.8
    _WATCH_GLITCH_SECONDS = 0.18
    _WATCH_ERROR_HOLD_SECONDS = 0.18
    _WATCH_REC_BLINK_HZ = 2.0
    _WATCH_STATIC_DOTS = 0
    _WATCH_STATIC_DOTS_PULSE = 4

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._selected = 0
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._backdrop: MainMenuBackdrop = make_main_menu_backdrop()
        self._watch_text_bank = PursuerTextBank()
        self._watch_seed = 0x13579BDF
        self._watch_event_t = 0.0
        self._watch_glitch_t = 0.0
        self._watch_error_t = 0.0
        self._watch_error_text = ""
        self._watch_rec_t = 0.0

    def enter(self, params: SceneEnterParams = None) -> None:
        self._selected = 0
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._backdrop.enter()
        self._watch_seed = (0x13579BDF ^ (
            (int(self._state.seed_counter) + 1) * 97)) & 0xFFFFFFFF
        if self._watch_seed == 0:
            self._watch_seed = 1
        self._watch_event_t = 0.0
        self._watch_glitch_t = 0.0
        self._watch_error_t = 0.0
        self._watch_error_text = ""
        self._watch_rec_t = 0.0

    def update(self, dt: float) -> None:
        self._backdrop.update(dt)
        self._update_entity_watch(dt)
        if self._overlay != self._OVERLAY_NONE:
            self._update_overlay_input()
            return

        if self._state.controls.pressed(Action.NAV_UP):
            self._selected -= 1
        elif self._state.controls.pressed(Action.NAV_DOWN):
            self._selected += 1

        item_count = len(self._MENU_ITEMS)
        if item_count > 0:
            while self._selected < 0:
                self._selected += item_count
            while self._selected >= item_count:
                self._selected -= item_count

        if self._state.controls.pressed(Action.CONFIRM):
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
        return bool(self._state.profile_loaded)

    def _update_overlay_input(self) -> None:
        if self._overlay == self._OVERLAY_NEW_GAME_CONFIRM:
            if self._state.controls.pressed(Action.CANCEL):
                self._overlay = self._OVERLAY_NONE
                self._overlay_scroll = 0
                return
            if self._state.controls.pressed(Action.CONFIRM):
                self._state.start_new_game()
                self._nav.go(SceneId.DRIVE_PRESET)
            return

        body_lines = self._overlay_body_lines_for(self._overlay)
        self._clamp_overlay_scroll(body_lines)
        if self._state.controls.pressed(Action.NAV_UP):
            self._overlay_scroll -= 1
            self._clamp_overlay_scroll(body_lines)
        elif self._state.controls.pressed(Action.NAV_DOWN):
            self._overlay_scroll += 1
            self._clamp_overlay_scroll(body_lines)

        if (
            self._state.controls.pressed(Action.CANCEL)
            or self._state.controls.pressed(Action.CONFIRM)
        ):
            self._overlay = self._OVERLAY_NONE
            self._overlay_scroll = 0

    def _activate_selected_item(self) -> None:
        item_id, _ = self._MENU_ITEMS[self._selected]
        if item_id == self._ITEM_CONTINUE:
            if not self._has_continue():
                return
            self._nav.go(SceneId.DRIVE_PRESET)
            return
        if item_id == self._ITEM_NEW_GAME:
            if self._has_continue():
                self._open_overlay(self._OVERLAY_NEW_GAME_CONFIRM)
                return
            self._state.start_new_game()
            self._nav.go(SceneId.DRIVE_PRESET)
            return
        if item_id == self._ITEM_CONTROLS:
            self._open_overlay(self._OVERLAY_CONTROLS)
            return
        if item_id == self._ITEM_CREDITS:
            self._open_overlay(self._OVERLAY_CREDITS)
            return

    def _open_overlay(self, overlay_id: int) -> None:
        self._overlay = int(overlay_id)
        self._overlay_scroll = 0

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
            marker = "  "
            if selected:
                marker = "> "
            print(marker + label, x, y, color)
            y += 10
            i += 1

    def _draw_left_save_info(self, x: int, y: int, w: int, h: int) -> None:
        if not self._has_continue():
            return
        if self._overlay != self._OVERLAY_NONE:
            return
        selected_id, _ = self._MENU_ITEMS[self._selected]
        if selected_id != self._ITEM_CONTINUE:
            return

        split_y = y + 66
        line(x, split_y, x + w - 1, split_y, Color.DARK_GREY)
        print("ON CONTINUE", x + 3, split_y + 4, Color.LIGHT_GREY)
        profile = self._state.profile
        row_step = 8
        seed_row_y = y + h - 9
        row_y = seed_row_y - row_step * 3
        self._draw_kv_row(x, w, row_y, "HP", str(
            self._to_ui_int(profile.garage_hp)), Color.WHITE, Color.WHITE)
        self._draw_kv_row(x, w, row_y + row_step, "FUEL",
                          str(self._to_ui_int(profile.garage_fuel)), Color.WHITE, Color.WHITE)
        self._draw_kv_row(x, w, row_y + row_step * 2, "SCRAP",
                          str(profile.scrap), Color.LIGHT_GREY, Color.LIGHT_GREY)
        self._draw_kv_row(x, w, row_y + row_step * 3, "SEED",
                          str(self._state.seed_counter), Color.GREY, Color.GREY)

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
        if self._overlay == self._OVERLAY_CONTROLS:
            self._draw_controls_overlay()
            return
        if self._overlay == self._OVERLAY_CREDITS:
            self._draw_credits_overlay()
            return
        if self._overlay == self._OVERLAY_NEW_GAME_CONFIRM:
            self._draw_new_game_overlay()
            return

    def _draw_overlay_box(self, title: str, lines: list[str]) -> None:
        layout = self._overlay_layout()
        x = self._layout_int(layout, "box_x", 20)
        y = self._layout_int(layout, "box_y", 28)
        w = self._layout_int(layout, "box_w", 200)
        h = self._layout_int(layout, "box_h", 90)
        header_text_y = self._layout_int(layout, "header_text_y", 37)
        body_top = self._layout_int(layout, "body_top", 54)
        rect(x, y, w, h, Color.BLACK)
        rect(x + 1, y + 1, w - 2, h - 2, Color.DARK_GREY)
        rect(x + 4, y + 4, w - 8, 14, Color.BLACK)
        line(x + 4, y + 18, x + w - 5, y + 18, Color.GREY)
        print(title, text_center_x(title, margin_x=x + 4),
              header_text_y, Color.WHITE)
        self._draw_overlay_footer(layout)
        wrapped = self._overlay_wrap_lines(lines, layout)
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
            print(wrapped[src_i], body_x, draw_y, Color.LIGHT_GREY)
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
        if overlay_id == self._OVERLAY_CONTROLS:
            return self._controls_overlay_lines()
        if overlay_id == self._OVERLAY_CREDITS:
            return self._credits_overlay_lines()
        if overlay_id == self._OVERLAY_NEW_GAME_CONFIRM:
            return self._new_game_overlay_lines()
        return []

    def _overlay_layout(self) -> dict:
        layout = self._OVERLAY_LAYOUTS.get(self._overlay)
        if layout is None:
            return self._OVERLAY_LAYOUT_DEFAULT
        return layout

    @staticmethod
    def _layout_int(layout: dict, key: str, fallback: int) -> int:
        value = layout.get(key)
        if value is None:
            return int(fallback)
        return int(value)

    @staticmethod
    def _layout_slot_index(
        layout: dict,
        key: str,
        fallback: int,
        slot_count: int
    ) -> int:
        idx = int(fallback)
        value = layout.get(key)
        if value is not None:
            idx = int(value)
        if idx < 0:
            return 0
        if idx >= slot_count:
            return slot_count - 1
        return idx

    @staticmethod
    def _layout_slot_weights(layout: dict, slot_count: int) -> list[int]:
        raw = layout.get("slot_weights")
        weights: list[int] = []
        i = 0
        while i < slot_count:
            w = 1
            if raw is not None and i < len(raw):
                w = int(raw[i])
                if w < 1:
                    w = 1
            weights.append(w)
            i += 1
        return weights

    def _draw_overlay_footer(self, layout: dict) -> None:
        x = self._layout_int(layout, "box_x", 20)
        w = self._layout_int(layout, "box_w", 200)
        footer_line_y = self._layout_int(layout, "footer_line_y", 104)
        footer_text_y = self._layout_int(layout, "footer_text_y", 108)
        button_bg_color = self._layout_int(layout, "footer_bg_color", 0)
        line(x + 4, footer_line_y, x + w - 5, footer_line_y, Color.GREY)
        inner_x = x + 4
        inner_w = w - 8
        slot_count = self._layout_int(layout, "slot_count", 4)
        if slot_count < 1:
            slot_count = 1
        slots = self._overlay_footer_slots(layout, slot_count)
        weights = self._layout_slot_weights(layout, slot_count)
        total_weight = 0
        i = 0
        while i < len(weights):
            total_weight += int(weights[i])
            i += 1
        if total_weight < 1:
            total_weight = slot_count

        slot_starts: list[int] = []
        slot_ends: list[int] = []
        acc = 0
        i = 0
        while i < slot_count:
            slot_x0 = inner_x + int(inner_w * acc / total_weight)
            acc += int(weights[i])
            slot_x1 = inner_x + int(inner_w * acc / total_weight)
            slot_starts.append(slot_x0)
            slot_ends.append(slot_x1)
            i += 1

        button_bg_y = footer_line_y + 2
        button_bg_h = footer_text_y + 8 - button_bg_y
        if button_bg_h < 1:
            button_bg_h = 1
        i = 0
        while i < slot_count:
            text = ""
            if i < len(slots):
                text = str(slots[i])
            if text != "":
                slot_x0 = slot_starts[i]
                slot_x1 = slot_ends[i]
                slot_w = slot_x1 - slot_x0
                if slot_w > 2:
                    rect(slot_x0 + 1, button_bg_y, slot_w - 2,
                         button_bg_h, button_bg_color)
            i += 1

        if self._OVERLAY_FOOTER_DEBUG_SLOTS:
            debug_y = footer_line_y + 1
            debug_h = 11
            debug_colors = [
                Color.DARK_BLUE,
                Color.BLUE,
                Color.DARK_GREEN,
                Color.PURPLE
            ]
            j = 0
            while j < slot_count:
                slot_x0 = slot_starts[j]
                slot_x1 = slot_ends[j]
                slot_w = slot_x1 - slot_x0
                rect(slot_x0, debug_y, slot_w, debug_h,
                     debug_colors[j % len(debug_colors)])
                print(str(j + 1), slot_x0 + 1, debug_y +
                      1, Color.YELLOW, fixed=True)
                j += 1
        split_color = Color.GREY
        if self._OVERLAY_FOOTER_DEBUG_SLOTS:
            split_color = Color.LIGHT_GREY
        j = 1
        while j < slot_count:
            split_x = slot_starts[j]
            line(
                split_x,
                footer_line_y + 1,
                split_x,
                footer_text_y + 7,
                split_color
            )
            j += 1
        i = 0
        while i < slot_count:
            text = ""
            if i < len(slots):
                text = str(slots[i])
            if text != "":
                slot_x0 = slot_starts[i]
                slot_x1 = slot_ends[i]
                slot_w = slot_x1 - slot_x0
                text_w = ui_rich_text_width(text)
                draw_x = slot_x0 + int((slot_w - text_w) * 0.5)
                ui_rich_print(
                    text,
                    draw_x,
                    footer_text_y,
                    Color.LIGHT_GREY,
                    fixed=True
                )
            i += 1

    def _overlay_footer_slots(self, layout: dict, slot_count: int) -> list[str]:
        slots: list[str] = []
        i = 0
        while i < slot_count:
            slots.append("")
            i += 1
        slot_nav = self._layout_slot_index(layout, "slot_nav", 0, slot_count)
        slot_confirm = self._layout_slot_index(
            layout, "slot_confirm", 2, slot_count)
        slot_cancel = self._layout_slot_index(
            layout, "slot_cancel", slot_count - 1, slot_count)

        if self._overlay == self._OVERLAY_NEW_GAME_CONFIRM:
            slots[slot_confirm] = ui_prompt_with_text(
                ui_prompt_for_action(self._state, Action.CONFIRM), "CONFIRM")
            slots[slot_cancel] = ui_prompt_with_text(
                ui_prompt_for_action(self._state, Action.CANCEL), "CANCEL")
            return slots
        if self._overlay == self._OVERLAY_CONTROLS:
            slots[slot_confirm] = ui_prompt_with_text(
                ui_prompt_for_action(self._state, Action.CONFIRM), "SAVE")
            slots[slot_cancel] = ui_prompt_with_text(
                ui_prompt_for_action(self._state, Action.CANCEL), "CANCEL")
            nav_prompt = ui_prompt_for_nav_hint(self._state)
            slots[slot_nav] = ui_prompt_with_text(nav_prompt, "NAV")
            return slots
        close_hint = ui_prompt_with_text(
            ui_prompt_for_action(self._state, Action.CANCEL), "CLOSE")
        slots[slot_cancel] = close_hint
        if self._overlay_max_scroll(self._overlay_body_lines_for(self._overlay), layout) > 0:
            nav_prompt = ui_prompt_for_nav_hint(self._state)
            slots[slot_nav] = ui_prompt_with_text(nav_prompt, "NAV")
        return slots

    def _overlay_max_chars_per_line(self, layout: dict = None) -> int:
        if layout is None:
            layout = self._overlay_layout()
        box_w = self._layout_int(layout, "box_w", 200)
        chars = int((box_w - self._OVERLAY_BODY_X_PAD * 2) / 6)
        if chars < 8:
            return 8
        return chars

    def _overlay_visible_lines(self, layout: dict = None) -> int:
        if layout is None:
            layout = self._overlay_layout()
        footer_line_y = self._layout_int(layout, "footer_line_y", 104)
        body_top = self._layout_int(layout, "body_top", 54)
        footer_cutoff = footer_line_y - 4
        body_h = footer_cutoff - body_top
        count = int(body_h / self._OVERLAY_BODY_LINE_STEP)
        if count < 1:
            return 1
        return count

    def _overlay_wrap_lines(self, lines: list[str], layout: dict = None) -> list[str]:
        max_chars = self._overlay_max_chars_per_line(layout)
        out: list[str] = []
        i = 0
        while i < len(lines):
            raw = str(lines[i])
            if raw == "":
                out.append("")
                i += 1
                continue
            rest = raw
            while len(rest) > max_chars:
                cut = max_chars
                probe = cut
                while probe > 0 and rest[probe - 1] != " ":
                    probe -= 1
                if probe < int(max_chars * 0.55):
                    probe = cut
                part = rest[:probe]
                part = part.strip()
                if part == "":
                    part = rest[:cut]
                    probe = cut
                out.append(part)
                rest = rest[probe:]
                rest = rest.lstrip()
            out.append(rest)
            i += 1
        return out

    def _overlay_max_scroll(self, lines: list[str], layout: dict = None) -> int:
        wrapped = self._overlay_wrap_lines(lines, layout)
        max_scroll = len(wrapped) - self._overlay_visible_lines(layout)
        if max_scroll < 0:
            return 0
        return max_scroll

    def _clamp_overlay_scroll(self, lines: list[str], layout: dict = None) -> None:
        max_scroll = self._overlay_max_scroll(lines, layout)
        if self._overlay_scroll < 0:
            self._overlay_scroll = 0
            return
        if self._overlay_scroll > max_scroll:
            self._overlay_scroll = max_scroll

    def _draw_controls_overlay(self) -> None:
        self._draw_overlay_box("CONTROLS", self._controls_overlay_lines())

    def _draw_credits_overlay(self) -> None:
        self._draw_overlay_box("CREDITS", self._credits_overlay_lines())

    def _draw_new_game_overlay(self) -> None:
        self._draw_overlay_box("CONFIRM RESET", self._new_game_overlay_lines())

    @staticmethod
    def _controls_overlay_lines() -> list[str]:
        return [
            "MENU: UP/DOWN OR DPAD",
            "CONFIRM: Z / A",
            "CANCEL: X / B",
            "",
            "DRIVE: ARROWS OR DPAD",
            "HAND BRAKE: X / LB",
            "DASH SKILL: Z / RB"
        ]

    @staticmethod
    def _credits_overlay_lines() -> list[str]:
        return [
            "WYRDWAY",
            "A GAME BY MARAT AZIZOV",
            "",
            "DESIGN / CODE / ART",
            "ETOMARAT",
            "",
            "THANKS FOR PLAYING"
        ]

    @staticmethod
    def _new_game_overlay_lines() -> list[str]:
        return [
            "START NEW GAME?",
            "CURRENT PROFILE PROGRESS",
            "WILL BE RESET",
            "",
            "THIS CANNOT BE UNDONE"
        ]


def make_main_menu_scene(nav: SceneNavigator) -> MainMenuScene:
    return MainMenuScene(nav)
