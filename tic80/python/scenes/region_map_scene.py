from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, print

    from ..contracts import DriveEnterParams, SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.poi_text import poi_type_label
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..core.ui.footer_slots import (
        ui_footer_slot_indices,
        ui_footer_slots_standard
    )
    from ..core.ui.overlay_footer import ui_overlay_footer_draw
    from ..core.ui.overlay_layout import OverlayLayout, ui_overlay_layout_centered
    from ..core.ui.overlay_runtime import UiOverlayRuntime
    from ..core.ui.overlay_modal import (
        ui_overlay_modal_draw_chrome
    )
    from ..core.ui.prompts import ui_prompt_for_action
    from ..data.tuning import TUNING
else:
    OverlayLayout = dict


class RegionMapScene:
    SCENE_ID = SceneId.REGION_MAP
    OVERLAY_W = 228
    OVERLAY_H = 124
    OVERLAY_HEADER_TEXT_OFFSET_Y = 9
    OVERLAY_BODY_TOP_OFFSET_Y = 24
    OVERLAY_FOOTER_LINE_OFFSET_Y = 110
    OVERLAY_FOOTER_TEXT_OFFSET_Y = 114
    COL_NODE_X = 16
    COL_SITE_X = 56
    COL_SCRAP_X = 148
    COL_FUEL_X = 188

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._ui = UiOverlayRuntime()
        self.selected_node = 1
        self.node_count = 5

    def enter(self, params: SceneEnterParams = None) -> None:
        self._ui.sync_actions(
            self._state.controls,
            [
                Action.NAV_UP,
                Action.NAV_DOWN,
                Action.NAV_LEFT,
                Action.NAV_RIGHT,
                Action.CONFIRM
            ]
        )
        self._ui.reset_footer()
        run = self._state.run
        if run is not None and run.node_id is not None:
            self.selected_node = run.node_id

    def _debug_seed_edit_enabled(self) -> bool:
        return self._state.debug_enabled

    def update(self, dt: float) -> None:
        self._ui.poll_mouse()
        nav_up_released = self._ui.poll_action(self._state.controls, Action.NAV_UP)
        nav_down_released = self._ui.poll_action(self._state.controls, Action.NAV_DOWN)
        nav_left_released = self._ui.poll_action(self._state.controls, Action.NAV_LEFT)
        nav_right_released = self._ui.poll_action(self._state.controls, Action.NAV_RIGHT)
        confirm_released = self._ui.poll_action(self._state.controls, Action.CONFIRM)
        debug_seed = self._debug_seed_edit_enabled()
        slot_count = 3 if debug_seed else 2
        slot_weights = (1, 1, 1) if debug_seed else (1, 1)
        layout = self._overlay_layout(slot_count, slot_weights)
        slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(layout, slot_count)
        slots = self._footer_slots(debug_seed)
        released_slot = self._ui.poll_footer_release(layout, slots)

        if nav_up_released:
            self.selected_node = max(1, self.selected_node - 1)
        if nav_down_released:
            self.selected_node = min(self.node_count, self.selected_node + 1)
        if self._debug_seed_edit_enabled():
            if nav_left_released:
                self._state.debug_shift_active_run_seed(-1)
            if nav_right_released:
                self._state.debug_shift_active_run_seed(1)
        if released_slot == slot_nav:
            self.selected_node += 1
            if self.selected_node > self.node_count:
                self.selected_node = 1
        if debug_seed and released_slot == slot_cancel:
            self._state.debug_shift_active_run_seed(1)
        if confirm_released or released_slot == slot_confirm:
            run = self._state.require_run()
            run.ensure_outbound_segment(
                self.selected_node,
                float(TUNING.DRIVE.segment_total_length)
            )
            run.ensure_delta(run.node_id)
            self._ui.reset_footer()
            self._nav.go(SceneId.DRIVE, DriveEnterParams("travel"))

    def _draw_node_row(self, run: RunState | None, node_id: int, y: int) -> None:
        marker = ">" if node_id == self.selected_node else " "
        if run is None:
            print(marker + " ID " + str(node_id), self.COL_NODE_X, y, Color.WHITE, True)
            return
        poi_type = run.preview_outbound_poi_type(node_id)
        poi_label = poi_type_label(poi_type).upper()
        rewards = run.preview_outbound_rewards(node_id)
        row_text = marker + " ID " + str(node_id)
        scrap_text = "+" + str(rewards.scrap)
        fuel_text = "+" + str(rewards.fuel)
        print(row_text, self.COL_NODE_X, y, Color.WHITE, True)
        print(poi_label, self.COL_SITE_X, y, Color.WHITE, True)
        print(scrap_text, self.COL_SCRAP_X, y, Color.LIGHT_GREEN, True)
        print(fuel_text, self.COL_FUEL_X, y, Color.YELLOW, True)

    def _fmt_hex32(self, value: int) -> str:
        return hex(int(value) & 0xFFFFFFFF)

    def _hud_line(self, run: RunState | None) -> str:
        if run is not None:
            hp = "HP " + f"{run.car_hp:.1f}"
            fuel = "FUEL " + f"{run.car_fuel:.1f}"
        else:
            hp = "HP " + f"{self._state.profile.garage_hp:.1f}"
            fuel = "FUEL " + f"{self._state.profile.garage_fuel:.1f}"
        scrap = "SCRAP " + str(self._state.profile.scrap)
        return hp + "   " + fuel + "   " + scrap

    def _draw_debug_block(self, run: RunState | None, x: int, y: int, footer_line_y: int) -> int:
        if run is None:
            return y
        node_id = self.selected_node
        rewards = run.preview_outbound_rewards(node_id)
        poi_type = run.preview_outbound_poi_type(node_id)
        if y + 7 >= footer_line_y:
            return y
        seed_base = run.preview_outbound_seed_base(node_id)
        print("DEBUG: NODE " + str(node_id) + " " + poi_type_label(poi_type), x, y, Color.LIGHT_GREY)
        y += 8
        if y + 7 >= footer_line_y:
            return y
        print("SEED " + self._fmt_hex32(seed_base), x, y, Color.LIGHT_GREY)
        y += 8
        if y + 7 >= footer_line_y:
            return y
        print("LEN " + str(int(TUNING.DRIVE.segment_total_length)) + " S+" + str(rewards.scrap) + " F+" + str(rewards.fuel), x, y, Color.LIGHT_GREY)
        return y + 8

    def _overlay_layout(self, slot_count: int, slot_weights: tuple[int, ...]) -> OverlayLayout:
        return ui_overlay_layout_centered(
            self.OVERLAY_W,
            self.OVERLAY_H,
            self.OVERLAY_HEADER_TEXT_OFFSET_Y,
            self.OVERLAY_BODY_TOP_OFFSET_Y,
            self.OVERLAY_FOOTER_LINE_OFFSET_Y,
            self.OVERLAY_FOOTER_TEXT_OFFSET_Y,
            slot_count,
            slot_weights,
            0,
            1,
            slot_count - 1
        )

    def _nav_down(self) -> bool:
        return (
            self._state.controls.down(Action.NAV_UP)
            or self._state.controls.down(Action.NAV_DOWN)
            or self._state.controls.down(Action.NAV_LEFT)
            or self._state.controls.down(Action.NAV_RIGHT)
        )

    def _footer_slots(self, debug_seed: bool) -> list[str]:
        slot_count = 3 if debug_seed else 2
        slot_weights = (1, 1, 1) if debug_seed else (1, 1)
        layout = self._overlay_layout(slot_count, slot_weights)
        slots = ui_footer_slots_standard(
            layout,
            slot_count,
            self._state,
            Action.CONFIRM,
            Action.CONFIRM,
            True,
            "NAV",
            "GO",
            ""
        )
        if debug_seed:
            _slot_nav, _slot_confirm, slot_cancel = ui_footer_slot_indices(layout, slot_count)
            seed_hint = ui_prompt_for_action(self._state, Action.NAV_LEFT) + "/" + ui_prompt_for_action(self._state, Action.NAV_RIGHT) + " SEED"
            slots[slot_cancel] = seed_hint
        return slots

    def draw(self) -> None:
        cls(Color.BLACK)
        run = self._state.run
        debug_seed = self._debug_seed_edit_enabled()
        slot_count = 3 if debug_seed else 2
        slot_weights = (1, 1, 1) if debug_seed else (1, 1)
        layout = self._overlay_layout(slot_count, slot_weights)
        box_x, _box_y, _box_w, _box_h, body_top, footer_line_y, footer_text_y = ui_overlay_modal_draw_chrome(
            layout,
            "REGION MAP",
            Color.WHITE,
            Color.BLACK,
            Color.DARK_GREY,
            Color.BLACK,
            Color.GREY
        )
        x = box_x + 8
        y = body_top
        print(self._hud_line(run), x, y, Color.WHITE)
        y += 10
        if run is not None:
            print("RUN SEED " + str(run.seed), x, y, Color.LIGHT_GREY)
            y += 10
        print("NODE", self.COL_NODE_X, y, Color.LIGHT_BLUE, True)
        print("SITE", self.COL_SITE_X, y, Color.LIGHT_BLUE, True)
        print("SCRAP", self.COL_SCRAP_X, y, Color.LIGHT_BLUE, True)
        print("FUEL", self.COL_FUEL_X, y, Color.LIGHT_BLUE, True)
        y += 8
        for i in range(self.node_count):
            node_id = i + 1
            self._draw_node_row(run, node_id, y)
            y += 8
        if self._state.debug_overlay_enabled:
            y += 2
            self._draw_debug_block(run, x, y, footer_line_y)
        slots = self._footer_slots(debug_seed)
        keyboard_active = [
            self._nav_down(),
            self._state.controls.down(Action.CONFIRM)
        ]
        if debug_seed:
            keyboard_active.append(
                self._state.controls.down(Action.NAV_LEFT)
                or self._state.controls.down(Action.NAV_RIGHT)
            )
        slot_active, slot_hover = self._ui.slot_states(
            len(slots),
            keyboard_active
        )
        ui_overlay_footer_draw(
            layout,
            slots,
            slot_active,
            slot_hover,
            footer_line_y,
            footer_text_y,
            Color.BLACK,
            Color.GREY
        )

    def exit(self) -> None:
        pass


def make_region_map_scene(nav: SceneNavigator) -> RegionMapScene:
    return RegionMapScene(nav)
