from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams, SceneEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


class RegionMapScene:
    SCENE_ID = SceneId.REGION_MAP
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
        if btnp(Button.UP):
            self.selected_node = max(1, self.selected_node - 1)
        if btnp(Button.DOWN):
            self.selected_node = min(self.node_count, self.selected_node + 1)
        if self._debug_seed_edit_enabled():
            if btnp(Button.LEFT):
                self._state.debug_shift_active_run_seed(-1)
            if btnp(Button.RIGHT):
                self._state.debug_shift_active_run_seed(1)
        if btnp(Button.A):
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
            print(marker + " ID " + str(node_id), 64, y, Color.WHITE, True)
            return
        poi_type = run.preview_outbound_poi_type(node_id)
        poi_label = self._poi_type_label(poi_type).upper()
        rewards = run.preview_outbound_rewards(node_id)
        row_text = marker + " ID " + str(node_id) + " " + poi_label
        scrap_text = "SCRAP +" + str(rewards.scrap)
        fuel_text = "FUEL +" + str(rewards.fuel)
        print(row_text, self.NODE_COL_X, y, Color.WHITE, True)
        print(scrap_text, self.SCRAP_COL_X, y, Color.WHITE, True)
        print(fuel_text, self.FUEL_COL_X, y, Color.WHITE, True)

    def _fmt_hex32(self, value: int) -> str:
        return hex(int(value) & 0xFFFFFFFF)

    def _poi_type_label(self, poi_type: str) -> str:
        if poi_type == "gas_station":
            return "gas station"
        if poi_type == "scrapyard":
            return "scrapyard"
        if poi_type == "depot":
            return "depot"
        return poi_type

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
              self._poi_type_label(poi_type), x, y, Color.WHITE, True)
        y += 8
        print("planned=" + planned + " route=" +
              route_label, x, y, Color.WHITE, True)
        y += 8
        print("seed_base=" + self._fmt_hex32(seed_base), x, y, Color.WHITE, True)
        y += 8
        print("base_rng=" + self._fmt_hex32(seed_base_rng),
              x, y, Color.WHITE, True)
        y += 8
        print("threat_rng=" + self._fmt_hex32(seed_threat_rng),
              x, y, Color.WHITE, True)
        y += 8
        print("len=" + str(int(len_units)) + " scrap=+" +
              str(rewards.scrap) + " fuel=+" + str(rewards.fuel), x, y, Color.WHITE, True)

    def draw(self) -> None:
        cls(Color.BLACK)
        print("REGION MAP (WIP PLACEHOLDER)", 44, 30, Color.WHITE, True)
        run = self._state.run
        if run is not None:
            print("seed=" + str(run.seed), 90, 40, Color.WHITE, True)
            print("fuel=" + f"{run.car_fuel:.2f}", 8, 8, Color.WHITE, True)
            print("hp=" + f"{run.car_hp:.2f}", 90, 8, Color.WHITE, True)
        else:
            print(
                "fuel=" + f"{self._state.profile.garage_fuel:.2f}", 8, 8, Color.WHITE, True)
            print("hp=" + f"{self._state.profile.garage_hp:.2f}",
                  90, 8, Color.WHITE, True)
        print("scrap=" + str(self._state.profile.scrap),
              170, 8, Color.WHITE, True)
        for i in range(self.node_count):
            node_id = i + 1
            self._draw_node_row(run, node_id, 48 + i * 8)
        if self._state.debug_overlay_enabled:
            self._draw_selected_node_details(run)
        if self._debug_seed_edit_enabled():
            print("L/R +/-1", 4, 128, Color.LIGHT_GREY, True)
        print("Z = GO", 96, 128, Color.WHITE, True)

    def exit(self) -> None:
        pass


def make_region_map_scene(nav: SceneNavigator) -> RegionMapScene:
    return RegionMapScene(nav)
