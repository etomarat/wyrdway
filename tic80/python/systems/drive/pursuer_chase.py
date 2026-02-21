from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ...contracts import PursuerVariantId, PursuerVariantTuning
    from ...core.run_state import RunState
    from ...data.tuning import TUNING
    from ...data.tuning.pursuers import pursuer_profile_for_variant
    from .drive_logic_core import DriveLogic


PursuerState = Literal["FAR", "CHASE", "NEAR"]
StrikePhase = Literal["SCRAP_HP", "FUEL"]

class PursuerStrikeEvent:
    __slots__ = ("_scrap_loss", "_fuel_loss", "_hp_loss")

    def __init__(self) -> None:
        self._scrap_loss = 0
        self._fuel_loss = 0
        self._hp_loss = 0

    @property
    def scrap_loss(self) -> int:
        return self._scrap_loss

    @property
    def fuel_loss(self) -> int:
        return self._fuel_loss

    @property
    def hp_loss(self) -> int:
        return self._hp_loss

    def clear(self) -> None:
        self._scrap_loss = 0
        self._fuel_loss = 0
        self._hp_loss = 0

    def set_losses(self, scrap_loss: int, fuel_loss: int, hp_loss: int) -> None:
        self._scrap_loss = max(0, int(scrap_loss))
        self._fuel_loss = max(0, int(fuel_loss))
        self._hp_loss = max(0, int(hp_loss))

    def happened(self) -> bool:
        return self._scrap_loss > 0 or self._fuel_loss > 0 or self._hp_loss > 0


class PursuerChase:
    __slots__ = (
        "_active",
        "_state",
        "_phase",
        "_grace_start_s",
        "_grace_elapsed",
        "_grace_active",
        "_pursuer_s",
        "_dist_s",
        "_cooldown",
        "_strike_flash",
        "_last_speed",
        "_strike_event",
        "_profile"
    )

    def __init__(self) -> None:
        self._active = False
        self._state: PursuerState = "FAR"
        self._phase: StrikePhase = "SCRAP_HP"
        self._grace_start_s = 0.0
        self._grace_elapsed = 0.0
        self._grace_active = False
        self._pursuer_s = 0.0
        self._dist_s = 9999.0
        self._cooldown = 0.0
        self._strike_flash = 0.0
        self._last_speed = 0.0
        self._strike_event = PursuerStrikeEvent()
        self._profile = pursuer_profile_for_variant(PursuerVariantId.ENTITY)

    @property
    def active(self) -> bool:
        return self._active

    @property
    def state(self) -> PursuerState:
        return self._state

    @property
    def phase(self) -> StrikePhase:
        return self._phase

    @property
    def grace_start_s(self) -> float:
        return self._grace_start_s

    @property
    def grace_elapsed(self) -> float:
        return self._grace_elapsed

    @property
    def in_grace(self) -> bool:
        return self._grace_active

    @property
    def distance_s(self) -> float:
        return self._dist_s

    @property
    def pursuer_s(self) -> float:
        return self._pursuer_s

    @property
    def cooldown(self) -> float:
        return self._cooldown

    @property
    def strike_flash(self) -> float:
        return self._strike_flash

    @property
    def last_speed(self) -> float:
        return self._last_speed

    @property
    def strike_event(self) -> PursuerStrikeEvent:
        return self._strike_event

    def near_intensity(self) -> float:
        p = self._active_profile()
        show = float(p.show_dist_s)
        near = float(p.near_dist_s)
        d = self._dist_s
        if d >= show:
            return 0.0
        if d <= near:
            return 1.0
        span = show - near
        if span <= 0.0001:
            return 0.0
        n = (show - d) / span
        if n < 0.0:
            return 0.0
        if n > 1.0:
            return 1.0
        return n

    def _active_profile(self) -> PursuerVariantTuning:
        if self._profile is None:
            return pursuer_profile_for_variant(PursuerVariantId.ENTITY)
        return self._profile

    def start_return(self, car_s: float, profile: PursuerVariantTuning) -> None:
        self._profile = profile
        p = self._active_profile()
        self._active = bool(TUNING.PURSUER.enabled)
        self._state = "FAR"
        self._phase = "SCRAP_HP"
        self._grace_start_s = float(car_s)
        self._grace_elapsed = 0.0
        self._grace_active = True
        self._pursuer_s = float(car_s) - float(p.start_gap_s)
        self._dist_s = float(p.start_gap_s)
        self._cooldown = 0.0
        self._strike_flash = 0.0
        self._last_speed = 0.0
        self._strike_event.clear()

    def disable(self) -> None:
        self._active = False
        self._state = "FAR"
        self._grace_active = False
        self._dist_s = 9999.0
        self._cooldown = 0.0
        self._strike_flash = 0.0
        self._last_speed = 0.0
        self._strike_event.clear()

    def _in_grace(self, car_s: float) -> bool:
        grace_m = float(TUNING.PURSUER.grace_meters)
        grace_t = float(TUNING.PURSUER.grace_seconds_cap)
        meters_done = False
        time_done = False
        if grace_m <= 0.0:
            meters_done = True
        else:
            meters_done = (car_s - self._grace_start_s) >= grace_m
        if grace_t <= 0.0:
            time_done = True
        else:
            time_done = self._grace_elapsed >= grace_t
        if meters_done or time_done:
            return False
        return True

    def _clamp01(self, value: float) -> float:
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    def _apply_strike(self, run: "RunState") -> None:
        p = self._active_profile()
        fuel_phase_enabled = bool(p.strike_enable_fuel_phase)
        drain = int(p.strike_drain_amount)
        if drain <= 0:
            if fuel_phase_enabled:
                self._phase = "FUEL" if self._phase == "SCRAP_HP" else "SCRAP_HP"
            else:
                self._phase = "SCRAP_HP"
            self._cooldown = float(p.strike_cooldown_sec)
            self._strike_flash = float(p.strike_flash_seconds)
            self._strike_event.clear()
            return

        scrap_loss = 0
        fuel_loss = 0
        hp_loss = 0
        if self._phase == "FUEL" and fuel_phase_enabled:
            fuel_before = float(run.car_fuel)
            run.consume_fuel(float(drain))
            fuel_loss = int(fuel_before - float(run.car_fuel) + 0.0001)
        else:
            scrap_loss = run.drain_scrap(drain)
            rem = drain - scrap_loss
            if rem > 0 and bool(p.strike_drain_hp_after_scrap):
                hp_before = float(run.car_hp)
                run.apply_damage(float(rem))
                hp_loss = int(hp_before - float(run.car_hp) + 0.0001)

        self._strike_event.set_losses(scrap_loss, fuel_loss, hp_loss)
        if fuel_phase_enabled:
            self._phase = "FUEL" if self._phase == "SCRAP_HP" else "SCRAP_HP"
        else:
            self._phase = "SCRAP_HP"
        self._cooldown = float(p.strike_cooldown_sec)
        self._strike_flash = float(p.strike_flash_seconds)

    def update(
        self,
        dt: float,
        run: "RunState",
        logic: "DriveLogic",
        boost_pushback_event: bool
    ) -> None:
        self._strike_event.clear()
        if not self._active:
            self._grace_active = False
            return

        self._grace_elapsed += dt
        if self._cooldown > 0.0:
            self._cooldown -= dt
            if self._cooldown < 0.0:
                self._cooldown = 0.0
        if self._strike_flash > 0.0:
            self._strike_flash -= dt
            if self._strike_flash < 0.0:
                self._strike_flash = 0.0

        car_s = float(logic.road_s)
        self._grace_active = self._in_grace(car_s)
        p = self._active_profile()
        if self._grace_active:
            self._pursuer_s = car_s - float(p.start_gap_s)
            self._state = "FAR"
            self._dist_s = float(p.start_gap_s)
            return

        max_speed = float(TUNING.DRIVE.max_speed)
        speed_factor = 0.0
        if max_speed > 0.0001:
            speed_factor = float(logic.speed) / max_speed
        if speed_factor < 0.0:
            speed_factor = 0.0
        if speed_factor > 2.0:
            speed_factor = 2.0
        slow_factor = self._clamp01(1.0 - speed_factor)

        pursuer_speed = float(p.base_speed)
        pursuer_speed += slow_factor * float(p.slow_catchup)
        if logic.offroad:
            pursuer_speed += float(p.offroad_catchup)
        if pursuer_speed < 0.0:
            pursuer_speed = 0.0
        show = float(p.show_dist_s)
        near = float(p.near_dist_s)
        gap = float(p.follow_gap_s)
        if gap < 0.0:
            gap = 0.0

        self._last_speed = pursuer_speed
        self._pursuer_s += pursuer_speed * dt

        if boost_pushback_event:
            pushback = float(p.boost_pushback_s)
            if pushback > 0.0:
                self._pursuer_s -= pushback

        max_pursuer_s = car_s - gap
        if self._pursuer_s > max_pursuer_s:
            self._pursuer_s = max_pursuer_s

        dist = car_s - self._pursuer_s
        if dist < 0.0:
            dist = 0.0

        self._dist_s = dist
        if dist > show:
            self._state = "FAR"
        elif dist > near:
            self._state = "CHASE"
        else:
            self._state = "NEAR"

        min_speed = float(p.strike_min_speed)
        speed_ok = True
        if min_speed > 0.0:
            speed_ok = float(logic.speed) >= min_speed
        strike_dist = float(p.strike_begin_dist_s)
        if strike_dist < gap:
            strike_dist = gap
        close_enough = self._dist_s <= strike_dist
        if close_enough and self._cooldown <= 0.0 and speed_ok:
            self._apply_strike(run)
