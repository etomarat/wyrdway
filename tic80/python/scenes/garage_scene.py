from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, line, print, rect, rectb, time

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_center_x, text_width
    from ..core.ui_modal import (
        ui_modal_centered_box,
        ui_modal_draw_box,
        ui_modal_draw_lines
    )
    from ..data.tuning import TUNING


class GarageScene:
    SCENE_ID = SceneId.GARAGE
    RETURN_HEADER_OPTIONS = [
        "WELCOME BACK // GARAGE LIGHTS ON",
        "WELCOME BACK // HOME GARAGE",
        "WELCOME BACK // YOU MADE IT",
        "WELCOME HOME // SAFEHOUSE",
        "BACK HOME // GARAGE LIGHTS ON"
    ]
    HOME_HEADER_TEXT = RETURN_HEADER_OPTIONS[0]
    VEHICLE_PANEL_X = 8
    VEHICLE_PANEL_Y = 24
    VEHICLE_PANEL_W = 224
    VEHICLE_PANEL_H = 50
    VEHICLE_DIVIDER_X = 154
    VEHICLE_DIVIDER_TOP = 30
    VEHICLE_DIVIDER_BOTTOM = 68
    VEHICLE_LEFT_X = 16
    VEHICLE_RIGHT_X = 162
    VEHICLE_NAME_Y = 29
    VEHICLE_HP_LABEL_Y = 37
    VEHICLE_HP_BAR_Y = 45
    VEHICLE_FUEL_LABEL_Y = 56
    VEHICLE_FUEL_BAR_Y = 63
    VEHICLE_BAR_W = 132
    VEHICLE_METER_BAR_H = 7
    MODAL_W = 188
    MODAL_H = 64

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._profile = nav.state.profile
        self._confirm_new_game = False
        self._rollback_modal_open = False
        self._rollback_modal_reason = ""
        self._rollback_modal_gain = 0
        self._header_text = self.HOME_HEADER_TEXT
        self._header_roll = 0

    def enter(self, params: SceneEnterParams = None) -> None:
        self._confirm_new_game = False
        reason, gain = self._state.consume_rollback_notice()
        self._rollback_modal_open = reason is not None
        self._rollback_modal_reason = "" if reason is None else str(reason)
        self._rollback_modal_gain = int(gain)
        self._pick_header_text()

    def _pick_header_text(self) -> None:
        if self._state.seed_counter <= 0:
            self._header_text = self.HOME_HEADER_TEXT
            return
        options = self.RETURN_HEADER_OPTIONS
        n = len(options)
        if n <= 0:
            self._header_text = self.HOME_HEADER_TEXT
            return
        self._header_roll += 1
        entropy = (
            int(time())
            + self._header_roll * 17
            + int(self._profile.scrap) * 7
            + int(self._profile.theseus) * 11
        )
        idx = entropy % n
        candidate = options[idx]
        if candidate == self._header_text and n > 1:
            idx = (idx + 1) % n
            candidate = options[idx]
        self._header_text = candidate

    def _clamp01(self, value: float) -> float:
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    def _fmt_num(self, value: float) -> str:
        return f"{float(value):.2f}"

    def _draw_meter(
        self,
        label: str,
        value: float,
        cap: float,
        x: int,
        y: int,
        w: int,
        fill_color: int,
        bar_h: int
    ) -> None:
        h = int(bar_h)
        if h < 4:
            h = 4
        inner_w = w - 2
        if inner_w < 1:
            inner_w = 1
        ratio = 0.0
        if cap > 0.0:
            ratio = self._clamp01(value / cap)
        fill_w = int(inner_w * ratio)
        rect(x, y, w, h, Color.BLACK)
        rect(x + 1, y + 1, inner_w, h - 2, Color.DARK_GREY)
        if fill_w > 0:
            rect(x + 1, y + 1, fill_w, h - 2, fill_color)
        rectb(x, y, w, h, Color.GREY)
        print(
            label + " " + self._fmt_num(value) + "/" + self._fmt_num(cap),
            x,
            y - 7,
            Color.LIGHT_GREY
        )

    def _repair_hint(self) -> tuple[str, int]:
        hp_max = float(TUNING.PROFILE.start_garage_hp)
        cost = int(TUNING.PROFILE.repair_cost)
        hp = float(self._profile.garage_hp)
        if hp >= hp_max:
            return "HP FULL", Color.LIGHT_GREY
        if self._profile.scrap < cost:
            return "NO SCRAP", Color.ORANGE
        return "READY", Color.LIGHT_GREEN

    def _draw_header_text(self, text: str, y: int, color: int) -> None:
        print(text, text_center_x(text, margin_x=4), y, color, True)

    def _draw_background(self) -> None:
        rect(0, 0, 240, 88, Color.DARK_GREY)
        rect(0, 88, 240, 48, Color.DARK_GREEN)
        y = 20
        while y < 89:
            line(0, y, 239, y, Color.BLACK)
            y += 12
        line(0, 88, 239, 88, Color.GREY)

    def _draw_header(self) -> None:
        rect(0, 0, 240, 15, Color.BLACK)
        line(0, 15, 239, 15, Color.GREY)
        self._draw_header_text(self._header_text, 5, Color.WHITE)

    def _draw_vehicle_panel(self) -> None:
        profile = self._profile
        hp_max = float(TUNING.PROFILE.start_garage_hp)
        fuel_cap = float(TUNING.PROFILE.start_garage_fuel)
        hp = float(profile.garage_hp)
        fuel = float(profile.garage_fuel)
        scrap = int(profile.scrap)
        repair_status, repair_color = self._repair_hint()

        rect(self.VEHICLE_PANEL_X, self.VEHICLE_PANEL_Y,
             self.VEHICLE_PANEL_W, self.VEHICLE_PANEL_H, Color.BLACK)
        rect(self.VEHICLE_PANEL_X + 1, self.VEHICLE_PANEL_Y + 1,
             self.VEHICLE_PANEL_W - 2, self.VEHICLE_PANEL_H - 2, Color.DARK_GREY)
        rectb(self.VEHICLE_PANEL_X, self.VEHICLE_PANEL_Y,
              self.VEHICLE_PANEL_W, self.VEHICLE_PANEL_H, Color.GREY)
        line(self.VEHICLE_DIVIDER_X, self.VEHICLE_DIVIDER_TOP,
             self.VEHICLE_DIVIDER_X, self.VEHICLE_DIVIDER_BOTTOM, Color.GREY)

        name_x = self.VEHICLE_LEFT_X
        name_y = self.VEHICLE_NAME_Y
        name = "LADA NIVA 4x4"
        trim = " 3-DOOR"
        print(name, name_x, name_y, Color.WHITE)
        print(trim, name_x + text_width(name), name_y, Color.LIGHT_GREY)
        self._draw_meter(
            "HP", hp, hp_max,
            self.VEHICLE_LEFT_X, self.VEHICLE_HP_BAR_Y, self.VEHICLE_BAR_W,
            Color.RED, self.VEHICLE_METER_BAR_H
        )
        self._draw_meter(
            "FUEL", fuel, fuel_cap,
            self.VEHICLE_LEFT_X, self.VEHICLE_FUEL_BAR_Y, self.VEHICLE_BAR_W,
            Color.YELLOW, self.VEHICLE_METER_BAR_H
        )

        print("SCRAP:", self.VEHICLE_RIGHT_X,
              self.VEHICLE_HP_LABEL_Y, Color.LIGHT_GREY)
        print(str(scrap), self.VEHICLE_RIGHT_X,
              self.VEHICLE_HP_BAR_Y + 1, Color.WHITE)
        print("REPAIR:", self.VEHICLE_RIGHT_X,
              self.VEHICLE_FUEL_LABEL_Y, Color.LIGHT_GREY)
        print(repair_status, self.VEHICLE_RIGHT_X,
              self.VEHICLE_FUEL_BAR_Y + 1, repair_color)

    def _draw_theseus_panel(self) -> None:
        theseus = int(self._profile.theseus)
        cap = 12.0
        ratio = self._clamp01(float(theseus) / cap)

        rect(8, 77, 224, 14, Color.BLACK)
        rect(9, 78, 222, 12, Color.DARK_GREY)
        rectb(8, 77, 224, 14, Color.LIGHT_BLUE)
        print("THESEUS", 16, 81, Color.LIGHT_BLUE)

        bar_x = 144
        bar_y = 80
        bar_w = 60
        bar_h = 7
        inner_w = bar_w - 2
        if inner_w < 1:
            inner_w = 1
        fill_w = int(inner_w * ratio)
        rect(bar_x, bar_y, bar_w, bar_h, Color.BLACK)
        rect(bar_x + 1, bar_y + 1, inner_w, bar_h - 2, Color.DARK_BLUE)
        if fill_w > 0:
            rect(bar_x + 1, bar_y + 1, fill_w, bar_h - 2, Color.LIGHT_BLUE)
        rectb(bar_x, bar_y, bar_w, bar_h, Color.GREY)
        print(str(theseus), 208, 81, Color.WHITE)

    def _draw_secondary_actions(self) -> None:
        repair_cost = int(TUNING.PROFILE.repair_cost)
        rect(8, 103, 224, 14, Color.BLACK)
        rect(9, 104, 222, 12, Color.DARK_GREY)
        rectb(8, 103, 224, 14, Color.GREY)
        print("X: REPAIR (-" + str(repair_cost) + " SCRAP)", 14, 107, Color.YELLOW)
        print("A: NEW GAME", 168, 107, Color.ORANGE)

    def _draw_start_cta(self) -> None:
        rect(6, 119, 228, 14, Color.LIGHT_GREEN)
        rectb(6, 119, 228, 14, Color.WHITE)
        text = "Z: START RUN"
        print(text, text_center_x(text, margin_x=6), 124, Color.BLACK)

    def _draw_rollback_popup(self) -> None:
        if not self._rollback_modal_open:
            return
        box_w = self.MODAL_W
        box_h = self.MODAL_H
        box_x, box_y = ui_modal_centered_box(box_w, box_h)
        ui_modal_draw_box(box_x, box_y, box_w, box_h, Color.ORANGE)
        lines = (
            ("ROLLBACK RECOVERED", Color.ORANGE),
            (self._rollback_modal_reason, Color.LIGHT_GREY),
            ("THESEUS +" + str(self._rollback_modal_gain), Color.RED),
            ("X: CLOSE", Color.LIGHT_GREY)
        )
        ui_modal_draw_lines(lines, box_x, box_y, box_w, 10, 12)

    def _draw_new_game_confirm(self) -> None:
        box_w = self.MODAL_W
        box_h = self.MODAL_H
        box_x, box_y = ui_modal_centered_box(box_w, box_h)
        ui_modal_draw_box(box_x, box_y, box_w, box_h, Color.WHITE)
        lines = (
            ("START NEW GAME?", Color.WHITE),
            ("THIS RESETS PROFILE PROGRESS", Color.LIGHT_GREY),
            ("Z: CONFIRM RESET", Color.RED),
            ("X: CANCEL / A: CANCEL", Color.LIGHT_GREY)
        )
        ui_modal_draw_lines(lines, box_x, box_y, box_w, 10, 12)

    def update(self, dt: float) -> None:
        if self._rollback_modal_open:
            if btnp(Button.B):
                self._rollback_modal_open = False
            return

        if self._confirm_new_game:
            if btnp(Button.A):
                self._state.start_new_game()
                self._confirm_new_game = False
                self._pick_header_text()
            elif btnp(Button.B) or btnp(Button.X):
                self._confirm_new_game = False
            return

        if btnp(Button.A):
            self._state.start_run()
            self._nav.go(SceneId.REGION_MAP)
        elif btnp(Button.B):
            repaired = self._profile.repair(
                TUNING.PROFILE.repair_cost,
                TUNING.PROFILE.repair_hp,
                TUNING.PROFILE.start_garage_hp
            )
            if repaired:
                self._state.save_profile()
        elif btnp(Button.X):
            self._confirm_new_game = True

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_background()
        self._draw_header()
        self._draw_vehicle_panel()
        self._draw_theseus_panel()
        self._draw_secondary_actions()
        self._draw_start_cta()
        self._draw_rollback_popup()
        if self._confirm_new_game:
            self._draw_new_game_confirm()

    def exit(self) -> None:
        pass


def make_garage_scene(nav: SceneNavigator) -> GarageScene:
    return GarageScene(nav)
