from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..core.ui.prompts import ui_prompt_for_action
    from ..core.ui.prompts import ui_prompt_with_text
    from ..core.ui.rich_text import ui_rich_print
    from ..data.tuning import TUNING
    from ..systems.drive.drive_input import read_drive_input
    from ..systems.drive.drive_logic_core import DriveLogic
    from ..systems.drive.drive_obstacle_hits import apply_obstacle_hits
    from ..systems.drive.drive_objects import DriveObjects, DriveZone
    from ..systems.drive.pursuer_chase import PursuerChase, PursuerState, PursuerStrikeDelta
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
        self._state.controls.enter_context(
            [
                Action.CONFIRM,
                Action.NAV_LEFT,
                Action.NAV_RIGHT,
                Action.THROTTLE,
                Action.BRAKE,
                Action.HANDBRAKE,
                Action.MODULE
            ],
            True
        )
        self._state.clear_drive_feedback()
        self._pursuer_archetype = create_active_pursuer_archetype()
        self._mode = params.mode
        self._evacuated = False
        self._road = None
        self._logic = None
        self._objects = None
        self._active_zone = None
        self._popups = []
        self._pursuer_fx_time = 0.0

        run = self._state.require_run()
        self._state.mark_run_active()
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
        if self._mode == "extract" and self._logic is not None:
            self._state.mark_chase_active()
            self._pursuer.start_return(self._logic.road_s, self._pursuer_archetype.profile)
        else:
            self._pursuer.disable()

        if TUNING.DRIVE.telemetry_enabled:
            self._telemetry = DriveTelemetry(
                int(TUNING.DRIVE.telemetry_every_frames),
                int(TUNING.DRIVE.telemetry_max_lines)
            )
            self._telemetry.begin(run.seed, self._mode, TUNING)
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
        zones = self._objects.zones_items()
        z_before = zone_at_hitboxes(self._logic, zones)
        apply_zone_effects(self._logic, z_before, TUNING)

        allow_dash = not self._logic.finished()
        inp = read_drive_input(self._state.controls, allow_dash)
        was_offroad = self._logic.offroad
        self._logic.update(dt, inp.steer, inp.throttle, inp.brake, inp.handbrake, inp.dash_pressed)
        self._update_offroad_transition_haptics(was_offroad)
        z_after = zone_at_hitboxes(self._logic, zones)
        self._active_zone = z_after if z_after is not None else z_before
        self._update_booster_enter_haptics(z_before, z_after)

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
                self._evacuate("OUT OF FUEL")
                return
            if run.car_hp <= 0:
                self._evacuate("CAR DESTROYED")
                return

        if self._logic.finished() and inp.a_pressed:
            if self._telemetry is not None:
                self._telemetry.dump("finish")
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
                return

            self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def _apply_obstacle_hits(self, run: RunState) -> None:
        road = self._road
        logic = self._logic
        objects = self._objects
        if road is None or logic is None or objects is None:
            return
        apply_obstacle_hits(run, road, logic, objects, TUNING, self._notify_obstacle_hit)

    def _notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        hitbox_radius: float
    ) -> None:
        self._renderer.notify_obstacle_hit(
            contact_wx,
            contact_wy,
            normal_x,
            normal_y,
            impact,
            hitbox_radius
        )
        self._state.vibe_obstacle_hit(impact)

    def _boost_pushback_event(self, z_before: DriveZone | None, z_after: DriveZone | None) -> bool:
        if z_before is not None or z_after is None:
            return False
        if TUNING.DRIVE.zone_boost_forward_accel <= 0.0 and TUNING.DRIVE.zone_boost_center_accel <= 0.0:
            return False
        return True

    def _update_offroad_transition_haptics(self, was_offroad: bool) -> None:
        logic = self._logic
        if logic is None:
            return
        if was_offroad or not logic.offroad:
            return
        max_speed = float(TUNING.DRIVE.feedback_speed_ref)
        speed_n = 0.0
        if max_speed > 0.0:
            speed_n = float(logic.speed) / max_speed
        self._state.vibe_offroad_transition(speed_n)

    def _update_booster_enter_haptics(
        self,
        z_before: DriveZone | None,
        z_after: DriveZone | None
    ) -> None:
        logic = self._logic
        if logic is None:
            return
        if not self._boost_pushback_event(z_before, z_after):
            return
        max_speed = float(TUNING.DRIVE.feedback_speed_ref)
        speed_n = 0.0
        if max_speed > 0.0:
            speed_n = float(logic.speed) / max_speed
        self._state.vibe_booster_enter(speed_n)

    def _append_popup(self, text: str, color: int) -> None:
        self._popups.append(_DrivePopup(text, color))

    @staticmethod
    def _whole_loss(value: float) -> int:
        if value <= 0.0:
            return 0
        return int(value + 0.0001)

    def _append_strike_popups(
        self,
        strike_delta: PursuerStrikeDelta,
        fuel_loss: int,
        hp_loss: int
    ) -> None:
        if strike_delta.scrap_loss > 0:
            self._append_popup("-" + str(strike_delta.scrap_loss) + " SCRAP", Color.LIGHT_GREEN)
        if fuel_loss > 0:
            self._append_popup("-" + str(fuel_loss) + " FUEL", Color.YELLOW)
        if hp_loss > 0:
            self._append_popup("-" + str(hp_loss) + " HP", Color.RED)

    def _apply_pursuer_strike_delta(self, run: RunState, strike_delta: PursuerStrikeDelta) -> None:
        if strike_delta.scrap_loss > 0:
            run.drain_scrap(strike_delta.scrap_loss)
        if strike_delta.fuel_drain > 0.0:
            run.consume_fuel(strike_delta.fuel_drain)
        if strike_delta.hp_damage > 0.0:
            run.apply_damage(strike_delta.hp_damage)

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
        if self._mode != "extract":
            return
        logic = self._logic
        if logic is None:
            return
        self._pursuer_fx_time += dt
        pushback_event = self._boost_pushback_event(z_before, z_after)
        strike_delta = self._pursuer.update(dt, run, logic, pushback_event)
        if strike_delta.has_runtime_effect():
            self._apply_pursuer_strike_delta(run, strike_delta)
        fuel_loss = self._whole_loss(strike_delta.fuel_drain)
        hp_loss = self._whole_loss(strike_delta.hp_damage)
        if strike_delta.scrap_loss > 0 or fuel_loss > 0 or hp_loss > 0:
            intensity = float(self._pursuer_archetype.profile.strike_shake_intensity)
            self._renderer.notify_pursuer_strike(intensity, self._pursuer_archetype.variant_id)
            self._state.vibe_pursuer_strike(hp_loss, intensity)
            if hp_loss > 0:
                self._renderer.notify_pursuer_hp_strike_fx(logic, hp_loss, intensity)
            self._append_strike_popups(strike_delta, fuel_loss, hp_loss)

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

        # Рендер держим отдельно от сцены, чтобы не раздувать DriveScene.
        pursuer_state: PursuerState | None = None
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
        self._state.vibe_drive_feedback(
            self._drive_gravel_strength(logic),
            self._renderer.exhaust_strength(),
            self._drive_drift_strength(logic)
        )
        if self._renderer.consume_start_move_event():
            self._state.vibe_burnout_start()
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
        self._ui.draw_controls_panel(self._state, logic)
        if self._pursuer.active:
            self._ui.draw_pursuer_hud(
                run.run_scrap(),
                self._start_run_scrap,
                self._pursuer.distance_s,
                self._pursuer.state,
                self._pursuer_archetype.profile,
                self._pursuer_archetype.display_name(),
                int(self._pursuer_archetype.profile.name_color)
        )
        self._draw_popups()
        if logic.finished():
            ui_rich_print(ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "CONTINUE"), 2, 128, Color.WHITE)
        if self._state.debug_enabled:
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
        if not self._popups:
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
        self._state.clear_drive_feedback()

    def _evacuate(self, reason: str) -> None:
        self._evacuated = True
        self._state.vibe_fail()
        if self._telemetry is not None:
            self._telemetry.dump("rollback fail " + reason)
        chase_contact = self._mode == "extract"
        self._state.rollback_to_last_save(reason, chase_contact)
        self._nav.go(SceneId.RESULT, ResultEnterParams("RUN FAILED"))

    @staticmethod
    def _drive_gravel_strength(logic: DriveLogic) -> float:
        if not logic.offroad:
            return 0.0
        speed_n = logic.dbg_speed_factor
        if speed_n <= 0.08:
            return 0.0
        strength = (speed_n - 0.08) / 0.40
        if strength <= 0.0:
            return 0.0
        if strength >= 1.0:
            return 1.0
        return strength

    @staticmethod
    def _drive_drift_strength(logic: DriveLogic) -> float:
        min_speed = TUNING.DRIVE.skid_min_speed
        speed = logic.speed
        if speed <= min_speed:
            return 0.0
        denom = abs(logic.v_forward) + TUNING.DRIVE.slip_eps_speed
        slip = abs(logic.v_side) / denom
        if slip > 1.0:
            slip = 1.0
        slip_threshold = TUNING.DRIVE.skid_slip_threshold
        drift_n = (slip - slip_threshold) / 0.55
        if drift_n <= 0.0 and logic.dbg_handbrake_decel <= 0.0:
            return 0.0
        speed_n = (speed - min_speed) / 28.0
        if speed_n <= 0.0:
            return 0.0
        if speed_n >= 1.0:
            speed_n = 1.0
        if drift_n <= 0.0:
            drift_n = 0.0
        elif drift_n >= 1.0:
            drift_n = 1.0
        if logic.dbg_handbrake_decel > 0.0 and drift_n < 0.38:
            drift_n = 0.38
        strength = drift_n * speed_n
        if strength >= 1.0:
            return 1.0
        return strength


def make_drive_scene(nav: SceneNavigator) -> DriveScene:
    return DriveScene(nav)
