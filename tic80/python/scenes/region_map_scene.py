from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, print

    from ..contracts import DriveEnterParams, SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.poi_text import poi_type_label
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_center_x
    from ..core.ui.panel import ui_panel_draw
    from ..core.ui.prompts import ui_prompt_for_action
    from ..core.ui.prompts import ui_prompt_with_text
    from ..core.ui.rich_text import ui_rich_print, ui_rich_text_center_x
    from ..data.tuning import TUNING


class RegionMapScene:
    SCENE_ID = SceneId.REGION_MAP
    TITLE_TEXT = "REGION MAP (WIP PLACEHOLDER)"
    TITLE_Y = 30
    TOP_PANEL_X = 4
    TOP_PANEL_Y = 2
    TOP_PANEL_W = 232
    TOP_PANEL_H = 14
    HUD_Y = 8
    HUD_FUEL_X = 8
    HUD_HP_X = 90
    HUD_SCRAP_X = 170
    ROW_BASE_Y = 48
    FOOTER_PANEL_X = 8
    FOOTER_PANEL_Y = 120
    FOOTER_PANEL_W = 224
    FOOTER_PANEL_H = 14
    NODE_COL_X = 10
    SCRAP_COL_X = 126
    FUEL_COL_X = 188

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self.selected_node = 1
        self.node_count = 5

    def enter(self, params: SceneEnterParams = None) -> None:
        run = self._state.run
        if run is not None and run.node_id is not None:
            self.selected_node = run.node_id

    def _debug_seed_edit_enabled(self) -> bool:
        return self._state.debug_enabled

    def update(self, dt: float) -> None:
        if self._state.controls.pressed(Action.NAV_UP):
            self.selected_node = max(1, self.selected_node - 1)
        if self._state.controls.pressed(Action.NAV_DOWN):
            self.selected_node = min(self.node_count, self.selected_node + 1)
        if self._debug_seed_edit_enabled():
            if self._state.controls.pressed(Action.NAV_LEFT):
                self._state.debug_shift_active_run_seed(-1)
            if self._state.controls.pressed(Action.NAV_RIGHT):
                self._state.debug_shift_active_run_seed(1)
        if self._state.controls.pressed(Action.CONFIRM):
            run = self._state.require_run()
            run.ensure_outbound_segment(
                self.selected_node,
                float(TUNING.DRIVE.segment_total_length)
            )
            run.ensure_delta(run.node_id)
            self._nav.go(SceneId.DRIVE, DriveEnterParams("travel"))

    def _draw_node_row(self, run: RunState | None, node_id: int, y: int) -> None:
        marker = ">" if node_id == self.selected_node else " "
        if run is None:
            print(marker + " ID " + str(node_id), 64, y, Color.WHITE)
            return
        poi_type = run.preview_outbound_poi_type(node_id)
        poi_label = poi_type_label(poi_type).upper()
        rewards = run.preview_outbound_rewards(node_id)
        row_text = marker + " ID " + str(node_id) + " " + poi_label
        scrap_text = "SCRAP +" + str(rewards.scrap)
        fuel_text = "FUEL +" + str(rewards.fuel)
        print(row_text, self.NODE_COL_X, y, Color.WHITE)
        print(scrap_text, self.SCRAP_COL_X, y, Color.WHITE)
        print(fuel_text, self.FUEL_COL_X, y, Color.WHITE)

    def _fmt_hex32(self, value: int) -> str:
        return hex(int(value) & 0xFFFFFFFF)

    def _draw_top_hud(self, run: RunState | None) -> None:
        ui_panel_draw(
            self.TOP_PANEL_X,
            self.TOP_PANEL_Y,
            self.TOP_PANEL_W,
            self.TOP_PANEL_H,
            Color.GREY,
            Color.BLACK,
            Color.DARK_GREY
        )
        if run is not None:
            print("fuel=" + f"{run.car_fuel:.2f}",
                  self.HUD_FUEL_X, self.HUD_Y, Color.WHITE)
            print("hp=" + f"{run.car_hp:.2f}",
                  self.HUD_HP_X, self.HUD_Y, Color.WHITE)
        else:
            print("fuel=" + f"{self._state.profile.garage_fuel:.2f}",
                  self.HUD_FUEL_X, self.HUD_Y, Color.WHITE)
            print("hp=" + f"{self._state.profile.garage_hp:.2f}",
                  self.HUD_HP_X, self.HUD_Y, Color.WHITE)
        print("scrap=" + str(self._state.profile.scrap),
              self.HUD_SCRAP_X, self.HUD_Y, Color.WHITE)

    def _draw_footer(self) -> None:
        ui_panel_draw(
            self.FOOTER_PANEL_X,
            self.FOOTER_PANEL_Y,
            self.FOOTER_PANEL_W,
            self.FOOTER_PANEL_H,
            Color.GREY,
            Color.BLACK,
            Color.BLACK
        )
        if self._debug_seed_edit_enabled():
            print("L/R +/-1", 14, 124, Color.LIGHT_GREY)
        prompt = ui_prompt_for_action(self._state, Action.CONFIRM)
        text = ui_prompt_with_text(prompt, "GO")
        ui_rich_print(text, ui_rich_text_center_x(text, margin_x=4), 124, Color.WHITE)

    def _draw_selected_node_details(self, run: RunState | None) -> None:
        if run is None:
            return
        node_id = self.selected_node
        rewards = run.preview_outbound_rewards(node_id)
        poi_type = run.preview_outbound_poi_type(node_id)
        plan = run.route_stack.find_outbound_by_target(node_id)

        planned = "no"
        route_label = "outbound"
        len_units = float(TUNING.DRIVE.segment_total_length)
        if plan is not None:
            planned = "yes"
            route_label = str(plan.leg_kind).lower()
            len_units = plan.len_units

        seed_base = run.preview_outbound_seed_base(node_id)
        seed_base_rng = seed_base ^ 0xA341316C
        seed_threat_rng = seed_base ^ 0x9E3779B9

        x = 4
        y = 90
        print("selected id=" + str(node_id) + " type=" +
              poi_type_label(poi_type), x, y, Color.WHITE)
        y += 8
        print("planned=" + planned + " route=" +
              route_label, x, y, Color.WHITE)
        y += 8
        print("seed_base=" + self._fmt_hex32(seed_base), x, y, Color.WHITE)
        y += 8
        print("base_rng=" + self._fmt_hex32(seed_base_rng),
              x, y, Color.WHITE)
        y += 8
        print("threat_rng=" + self._fmt_hex32(seed_threat_rng),
              x, y, Color.WHITE)
        y += 8
        print("len=" + str(int(len_units)) + " scrap=+" +
              str(rewards.scrap) + " fuel=+" + str(rewards.fuel), x, y, Color.WHITE)

    def draw(self) -> None:
        cls(Color.BLACK)
        print(self.TITLE_TEXT, text_center_x(
            self.TITLE_TEXT, margin_x=4), self.TITLE_Y, Color.WHITE, True)
        run = self._state.run
        self._draw_top_hud(run)
        if run is not None:
            print("seed=" + str(run.seed), 90, 40, Color.WHITE)
        for i in range(self.node_count):
            node_id = i + 1
            self._draw_node_row(run, node_id, self.ROW_BASE_Y + i * 8)
        if self._state.debug_overlay_enabled:
            self._draw_selected_node_details(run)
        self._draw_footer()

    def exit(self) -> None:
        pass


def make_region_map_scene(nav: SceneNavigator) -> RegionMapScene:
    return RegionMapScene(nav)
