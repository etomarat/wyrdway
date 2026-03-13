from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, print

    from ..contracts import DriveEnterParams, SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action, ActionId
    from ..core.palette import Color
    from ..core.poi_text import poi_type_label
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..core.ui.footer_slots import (
        ui_footer_slot_indices,
        ui_footer_slots_standard
    )
    from ..core.ui.input_layer import UiInputLayer
    from ..core.ui.overlay_layout import ui_overlay_layout_centered_by_spec
    from ..core.ui.overlay_screen import ui_overlay_screen_draw
    from ..data.tuning import TUNING
class RegionMapScene:
    SCENE_ID = SceneId.REGION_MAP
    OVERLAY_W = 228
    OVERLAY_H = 124
    OVERLAY_HEADER_TEXT_OFFSET_Y = 9
    OVERLAY_BODY_TOP_OFFSET_Y = 24
    OVERLAY_LAYOUT_SPEC = (
        OVERLAY_W,
        OVERLAY_H,
        OVERLAY_HEADER_TEXT_OFFSET_Y,
        OVERLAY_BODY_TOP_OFFSET_Y
    )
    COL_NODE_X = 16
    COL_SITE_X = 56
    COL_SCRAP_X = 148
    COL_FUEL_X = 188

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._ui = UiInputLayer()
        self.selected_node = 1
        self.node_count = 5

    def enter(self, params: SceneEnterParams = None) -> None:
        self._ui.reset_footer()
        self._apply_input_context(True)
        run = self._state.run
        if run is not None and run.node_id is not None:
            self.selected_node = run.node_id

    def _apply_input_context(self, swallow_held: bool) -> None:
        actions: list[ActionId] = [
            Action.NAV_UP,
            Action.NAV_DOWN,
            Action.NAV_LEFT,
            Action.NAV_RIGHT,
            Action.CONFIRM
        ]
        self._ui.activate(self._state.controls, actions, swallow_held)

    def update(self, dt: float) -> None:
        self._ui.poll_mouse()
        nav_up_released = self._ui.poll_action(self._state.controls, Action.NAV_UP)
        nav_down_released = self._ui.poll_action(self._state.controls, Action.NAV_DOWN)
        confirm_released = self._ui.poll_confirm(
            self._state, self._state.controls)
        slot_count = 2
        slot_weights = (1, 1)
        layout = ui_overlay_layout_centered_by_spec(
            self.OVERLAY_LAYOUT_SPEC,
            slot_count,
            slot_weights,
            0,
            1,
            slot_count - 1
        )
        slot_nav, slot_confirm, _slot_cancel = ui_footer_slot_indices(layout, slot_count)
        slots = self._footer_slots()
        released_slot = self._ui.poll_footer_release(layout, slots)

        if nav_up_released:
            self.selected_node = max(1, self.selected_node - 1)
        if nav_down_released:
            self.selected_node = min(self.node_count, self.selected_node + 1)
        if self._ui.footer_button_released(self._state, released_slot, slot_nav):
            self.selected_node += 1
            if self.selected_node > self.node_count:
                self.selected_node = 1
        if confirm_released or self._ui.footer_button_released(self._state, released_slot, slot_confirm):
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

    def _hud_line(self, run: RunState | None) -> str:
        if run is not None:
            hp = "HP " + f"{run.car_hp:.1f}"
            fuel = "FUEL " + f"{run.car_fuel:.1f}"
        else:
            hp = "HP " + f"{self._state.profile.garage_hp:.1f}"
            fuel = "FUEL " + f"{self._state.profile.garage_fuel:.1f}"
        scrap = "SCRAP " + str(self._state.profile.scrap)
        return hp + "   " + fuel + "   " + scrap

    def _nav_down(self) -> bool:
        return (
            self._ui.down(self._state.controls, Action.NAV_UP)
            or self._ui.down(self._state.controls, Action.NAV_DOWN)
            or self._ui.down(self._state.controls, Action.NAV_LEFT)
            or self._ui.down(self._state.controls, Action.NAV_RIGHT)
        )

    def _footer_slots(self) -> list[str]:
        slot_count = 2
        slot_weights = (1, 1)
        layout = ui_overlay_layout_centered_by_spec(
            self.OVERLAY_LAYOUT_SPEC,
            slot_count,
            slot_weights,
            0,
            1,
            slot_count - 1
        )
        return ui_footer_slots_standard(
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

    def draw(self) -> None:
        cls(Color.BLACK)
        run = self._state.run
        slot_count = 2
        slot_weights = (1, 1)
        layout = ui_overlay_layout_centered_by_spec(
            self.OVERLAY_LAYOUT_SPEC,
            slot_count,
            slot_weights,
            0,
            1,
            slot_count - 1
        )
        slots = self._footer_slots()
        keyboard_active = [
            self._nav_down(),
            self._ui.down(self._state.controls, Action.CONFIRM)
        ]
        box_x, _box_y, _box_w, _box_h, body_top, _footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            self._ui.runtime,
            layout,
            "REGION MAP",
            [],
            slots,
            keyboard_active
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

    def exit(self) -> None:
        pass


def make_region_map_scene(nav: SceneNavigator) -> RegionMapScene:
    return RegionMapScene(nav)
