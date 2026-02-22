from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from tic80 import cls, keyp, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneEnterParams, SceneNavigator
    from ..core.palette import Color
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING
    from ..systems.drive.drive_input import read_drive_input
    from ..systems.drive.drive_logic_core import DriveLogic
    from ..systems.drive.drive_obstacle_hits import apply_obstacle_hits
    from ..systems.drive.drive_objects import DriveObjects, DriveZone
    from ..systems.drive.pursuer_chase import PursuerChase, PursuerStrikeEvent
    from ..systems.drive.drive_telemetry import DriveTelemetry
    from ..systems.drive.drive_debug_lines import drive_debug_lines
    from ..systems.drive.drive_zone_effects import apply_zone_effects
    from ..systems.drive.drive_zones import zone_at_hitboxes
    from ..systems.drive.pursuers.archetypes import PursuerArchetype
    from ..systems.drive.pursuers.registry import create_active_pursuer_archetype
    from ..systems.drive.road_model import RoadModel
    from .drive.pursuer_screen_fx import PursuerScreenFx, PursuerScreenFxFrameState
    from .drive.drive_topdown_renderer import DriveTopdownRenderer
    from .drive.drive_ui import DriveUi


class _DrivePopup:
    __slots__ = ("text", "color", "ttl", "rise")

    def __init__(self, text: str, color: int) -> None:
        self.text = text
        self.color = color
        self.ttl = 0.75
        self.rise = 0.0


class DriveScene:
    SCENE_ID = SceneId.DRIVE

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._mode = "travel"
        self._variant = "topdown"
        self._road: RoadModel | None = None
        self._logic: DriveLogic | None = None
        self._objects: DriveObjects | None = None
        self._active_zone: DriveZone | None = None
        self._evacuated = False
        self._telemetry: DriveTelemetry | None = None
        self._renderer = DriveTopdownRenderer()
        self._pursuer_screen_fx = PursuerScreenFx()
        self._ui = DriveUi()
        self._start_car_hp = 0.0
        self._start_car_fuel = 0.0
        self._start_run_scrap = 0
        self._pursuer = PursuerChase()
        self._pursuer_archetype: PursuerArchetype = create_active_pursuer_archetype()
        self._popups: list[_DrivePopup] = []
        self._pursuer_fx_time = 0.0

    def enter(self, params: SceneEnterParams = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._pursuer_archetype = create_active_pursuer_archetype()
        self._mode = params.mode
        self._variant = params.variant
        self._evacuated = False
        self._road = None
        self._logic = None
        self._objects = None
        self._active_zone = None
        self._popups = []
        self._pursuer_fx_time = 0.0

        run = self._state.require_run()
        seed = run.seed
        segment_len = float(TUNING.DRIVE.segment_total_length)
        reverse_layout = False
        segment = run.active_segment
        if segment is not None:
            seed = segment.seed_base
            segment_len = segment.len_units
            reverse_layout = segment.leg_kind == "RETURN"
        self._road = RoadModel.from_tuning_with_length(seed, TUNING, segment_len)
        if reverse_layout:
            self._road.reverse_geometry_in_place()
        self._logic = DriveLogic(run, self._road, TUNING)
        spawn_threats = True
        if self._mode == "extract":
            spawn_threats = False
        self._objects = DriveObjects.from_road_and_tuning(
            seed,
            self._road,
            TUNING,
            spawn_threats,
            reverse_layout
        )
        self._start_car_hp = run.car_hp
        self._start_car_fuel = run.car_fuel
        self._start_run_scrap = run.run_scrap()
        if self._mode == "extract" and not self._state.playtest_enabled and self._logic is not None:
            self._pursuer.start_return(self._logic.road_s, self._pursuer_archetype.profile)
        else:
            self._pursuer.disable()

        if TUNING.DRIVE.telemetry_enabled:
            self._telemetry = DriveTelemetry(
                int(TUNING.DRIVE.telemetry_every_frames),
                int(TUNING.DRIVE.telemetry_max_lines)
            )
            self._telemetry.begin(run.seed, self._mode, self._variant, TUNING)
        else:
            self._telemetry = None

    def update(self, dt: float) -> None:
        run = self._state.run
        if run is None:
            return
        if self._logic is None:
            return
        if self._road is None:
            return
        if self._objects is None:
            return
        if self._state.playtest_enabled and keyp(18):
            self._restart_segment()
            return
        if self._state.playtest_enabled:
            self._state.playtest_add_time(dt)

        zones = self._objects.zones_items()
        z_before = zone_at_hitboxes(self._logic, zones)
        apply_zone_effects(self._logic, z_before, TUNING)

        allow_dash = not self._logic.finished()
        inp = read_drive_input(allow_dash)
        self._logic.update(dt, inp.steer, inp.throttle, inp.brake, inp.handbrake, inp.dash_pressed)
        z_after = zone_at_hitboxes(self._logic, zones)
        self._active_zone = z_after if z_after is not None else z_before

        self._apply_obstacle_hits(run)
        self._update_pursuer(dt, run, z_before, z_after)
        self._update_popups(dt)

        # Обновляем эффекты зон для СЛЕДУЮЩЕГО кадра (без 1-кадрового “залипания”).
        apply_zone_effects(self._logic, z_after, TUNING)
        if self._telemetry is not None:
            self._telemetry.after_update(
                dt,
                inp.steer,
                inp.throttle,
                inp.brake,
                inp.handbrake,
                inp.dash_pressed,
                run,
                self._logic
            )

        if not self._evacuated:
            if run.car_fuel <= 0:
                self._evacuate(run, "OUT OF FUEL")
                return
            if run.car_hp <= 0:
                self._evacuate(run, "CAR DESTROYED")
                return

        if self._logic.finished() and inp.a_pressed:
            if self._telemetry is not None:
                self._telemetry.dump("finish")
            if self._state.playtest_enabled:
                self._state.playtest_finish_segment()
                self._nav.go(SceneId.RESULT,
                             ResultEnterParams("SEGMENT COMPLETE"))
                return
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
                return

            delta = run.ensure_delta(run.node_id)
            delta.set_escape_outcome("ok")
            self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def _apply_obstacle_hits(self, run: RunState) -> None:
        road = self._road
        logic = self._logic
        objects = self._objects
        if road is None or logic is None or objects is None:
            return
        apply_obstacle_hits(run, road, logic, objects, TUNING, self._renderer.notify_obstacle_hit)

    def _boost_pushback_event(self, z_before: DriveZone | None, z_after: DriveZone | None) -> bool:
        if z_before is not None or z_after is None:
            return False
        if TUNING.DRIVE.zone_boost_forward_accel <= 0.0 and TUNING.DRIVE.zone_boost_center_accel <= 0.0:
            return False
        return True

    def _append_popup(self, text: str, color: int) -> None:
        self._popups.append(_DrivePopup(text, color))

    def _append_strike_popups(self, event: PursuerStrikeEvent) -> None:
        if event.scrap_loss > 0:
            self._append_popup("-" + str(event.scrap_loss) + " SCRAP", Color.LIGHT_GREEN)
        if event.fuel_loss > 0:
            self._append_popup("-" + str(event.fuel_loss) + " FUEL", Color.YELLOW)
        if event.hp_loss > 0:
            self._append_popup("-" + str(event.hp_loss) + " HP", Color.RED)

    def _update_popups(self, dt: float) -> None:
        i = len(self._popups) - 1
        while i >= 0:
            p = self._popups[i]
            p.ttl -= dt
            p.rise += dt * 14.0
            if p.ttl <= 0.0:
                del self._popups[i]
            i -= 1

    def _update_pursuer(
        self,
        dt: float,
        run: RunState,
        z_before: DriveZone | None,
        z_after: DriveZone | None
    ) -> None:
        if self._mode != "extract" or self._state.playtest_enabled:
            return
        logic = self._logic
        if logic is None:
            return
        self._pursuer_fx_time += dt
        pushback_event = self._boost_pushback_event(z_before, z_after)
        self._pursuer.update(dt, run, logic, pushback_event)
        event = self._pursuer.strike_event
        if event.happened():
            intensity = float(self._pursuer_archetype.profile.strike_shake_intensity)
            self._renderer.notify_pursuer_strike(intensity, self._pursuer_archetype.variant_id)
            if event.hp_loss > 0:
                self._renderer.notify_pursuer_hp_strike_fx(logic, event.hp_loss, intensity)
            self._append_strike_popups(event)

    def _restart_segment(self) -> None:
        run = self._state.run
        if run is None:
            return
        run.reset_car_stats(self._start_car_hp, self._start_car_fuel)
        mode: Literal["travel", "extract"] = "travel"
        if self._mode == "extract":
            mode = "extract"
        variant: Literal["topdown", "cockpit"] = "topdown"
        if self._variant == "cockpit":
            variant = "cockpit"
        self.enter(DriveEnterParams(mode, variant))

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_topdown()

    def _draw_topdown(self) -> None:
        """Top-down рендер DRIVE: дорога, зоны, препятствия, машина, подсказки."""
        logic = self._logic
        road = self._road
        run = self._state.run
        objects = self._objects
        if logic is None or road is None or run is None or objects is None:
            return

        # Рендер держим отдельно от сцены, чтобы позже легко подключить второй вид (cockpit)
        # и не раздувать DriveScene.
        pursuer_state: str | None = None
        pursuer_s = 0.0
        strike_flash = 0.0
        screen_glitch_active = False
        pursuer_fx_state: PursuerScreenFxFrameState | None = None
        if self._pursuer.active:
            pursuer_state = self._pursuer.state
            pursuer_s = self._pursuer.pursuer_s
            strike_flash = self._pursuer.strike_flash
            pursuer_fx_state = self._pursuer_screen_fx.build_frame_state(
                self._pursuer,
                self._pursuer_fx_time,
                self._pursuer_archetype.profile
            )
            screen_glitch_active = pursuer_fx_state.glitch_active

        self._renderer.draw(
            road,
            logic,
            objects,
            self._active_zone,
            self._pursuer_archetype,
            pursuer_state,
            pursuer_s,
            strike_flash,
            screen_glitch_active
        )
        if self._pursuer.active:
            # FX погони (виньетка/шум) рисуем ПОД HUD.
            self._pursuer_screen_fx.draw(
                logic,
                self._pursuer,
                self._pursuer_fx_time,
                self._pursuer_archetype.profile,
                pursuer_fx_state
            )
        self._ui.draw_stats(run, logic)
        self._ui.draw_steer_wheel(logic)
        self._ui.draw_slip_bar(logic)
        if self._pursuer.active:
            self._ui.draw_pursuer_hud(
                run.run_scrap(),
                self._start_run_scrap,
                self._pursuer.distance_s,
                self._pursuer.state,
                self._pursuer_archetype.profile,
                self._pursuer_archetype.display_name()
            )
        self._draw_popups()
        if logic.finished():
            print("Z = CONTINUE", 2, 128, Color.WHITE)
        else:
            print("ARROWS + X", 2, 128, Color.WHITE)
        lines = drive_debug_lines(road, logic, run, objects, TUNING)
        if self._pursuer.active:
            lines.append(
                "pursuer d="
                + str(round(self._pursuer.distance_s, 2))
                + " v="
                + str(round(self._pursuer.last_speed, 2))
                + " state="
                + self._pursuer.state
                + " cd="
                + str(round(self._pursuer.cooldown, 2))
                + " phase="
                + self._pursuer.phase
            )
        self._state.set_debug_lines(lines)
        return

    def _draw_popups(self) -> None:
        if len(self._popups) <= 0:
            return
        base_x = 96
        base_y = int(TUNING.DRIVE.view_center_y) - 18
        if base_y < 16:
            base_y = 16
        i = 0
        while i < len(self._popups):
            p = self._popups[i]
            y = base_y - int(p.rise) - i * 8
            print(p.text, base_x, y, p.color)
            i += 1

    def exit(self) -> None:
        pass

    def _evacuate(self, run: RunState, reason: str) -> None:
        if self._mode == "travel" and not self._state.playtest_enabled:
            self._evacuated = True
            if self._telemetry is not None:
                self._telemetry.dump("travel fail rollback " + reason)
            self._state.rollback_to_last_save()
            self._nav.go(SceneId.RESULT, ResultEnterParams("TRAVEL FAIL: ROLLBACK TO SAVE"))
            return

        delta = run.ensure_delta(run.node_id)
        delta.set_escape_outcome("fail")
        self._evacuated = True
        if self._telemetry is not None:
            self._telemetry.dump("evac " + reason)
        msg = reason
        if self._mode == "extract" and not self._state.playtest_enabled:
            msg = reason + " / LOOT LOST"
        self._nav.go(SceneId.RESULT, ResultEnterParams(msg))


def make_drive_scene(nav: SceneNavigator) -> DriveScene:
    return DriveScene(nav)
