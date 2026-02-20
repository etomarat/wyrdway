from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import DriveTuning
    from ...core.palette import Color
    from ..fx.fx_ids import FxId
    from ..fx.fx_manager import FxSystem
    from ..fx.vendor.vand_particles import VandParticles
    from ..fx.vendor.viza_presets import make_explosion_fx, make_smoke_fx
    from ..fx.vendor.viza_pslib import PslibFx
    from .drive_fx import DriveFx, _FxHitParams, _FxStartParams
    from .fx_particles import Particles2D
    from .rng import Rng


class _Particles2DFx(FxSystem):
    """Адаптер `Particles2D` под интерфейс `FxSystem`."""

    def __init__(self, p: Particles2D) -> None:
        self._p = p

    def alive(self) -> bool:
        return self._p.count() > 0

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        self._p.update(dt, world_dx, world_dy)

    def draw(self) -> None:
        self._p.draw()


class _StartDustFx(FxSystem):
    """Стартовый «дым из-под колёс» на базе `Particles2D`."""

    def __init__(
        self,
        d: DriveTuning,
        rng: Rng,
        fx: Particles2D,
        cx: float,
        cy: float,
        emit_seconds: float
    ) -> None:
        self._d = d
        self._rng = rng
        self._fx = fx
        self._cx = cx
        self._cy = cy
        self._t = emit_seconds
        self._acc = 0.0

    def alive(self) -> bool:
        return self._fx.count() > 0 or self._t > 0.0

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        d = self._d
        self._fx.update(dt, world_dx, world_dy)
        if self._t <= 0.0:
            return
        self._t -= dt
        if self._t < 0.0:
            self._t = 0.0

        self._acc += float(d.fx_dust_rate_start) * dt
        n = int(self._acc)
        if n <= 0:
            return
        self._acc -= n

        anchor_shift_x = 16.0 - float(d.car_sprite_anchor_x)
        anchor_shift_back = 16.0 - float(d.car_sprite_anchor_y)
        wheel_dx = float(d.fx_dust_wheel_dx_px) + anchor_shift_x
        back = float(d.fx_dust_back_px) + anchor_shift_back
        jitter_x = float(d.fx_dust_jitter_x_px)
        jitter_y = float(d.fx_dust_jitter_y_px)
        life = int(d.fx_dust_life_frames)
        if life <= 0:
            life = 1

        i = 0
        while i < n:
            jx = (self._rng.rand01() - 0.5) * jitter_x
            jy = (self._rng.rand01()) * jitter_y

            vx0 = (self._rng.rand01() - 0.5) * float(d.fx_dust_spread_vx)
            vy0 = (self._rng.rand01()) * float(d.fx_dust_spread_vy)

            x_l = (self._cx - wheel_dx) + jx
            y_l = (self._cy + back) + jy
            x_r = (self._cx + wheel_dx) - jx
            y_r = (self._cy + back) + jy

            color = d.fx_start_dust_color_a if (
                self._rng.next_u32() & 1) == 0 else d.fx_start_dust_color_b
            self._fx.spawn(x_l, y_l, 0.0, 0.0, vx0, vy0, life, color)
            self._fx.spawn(x_r, y_r, 0.0, 0.0, -vx0, vy0, life, color)
            i += 1

    def draw(self) -> None:
        self._fx.draw()


class _StartVandDustFx(FxSystem):
    """Стартовый дым на базе `VandParticles` (режим `dust_down`)."""

    def __init__(
        self,
        d: DriveTuning,
        v: VandParticles,
        rng: Rng,
        cx: float,
        cy: float,
        emit_seconds: float
    ) -> None:
        self._d = d
        self._v = v
        self._rng = rng
        self._cx = cx
        self._cy = cy
        self._t = emit_seconds
        self._acc = 0.0

    def alive(self) -> bool:
        return self._v.alive() or self._t > 0.0

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        d = self._d
        self._v.update(dt, world_dx, world_dy)
        if self._t <= 0.0:
            return
        self._t -= dt
        if self._t < 0.0:
            self._t = 0.0

        self._acc += float(d.fx_dust_rate_start) * dt
        n = int(self._acc)
        if n <= 0:
            return
        self._acc -= n

        anchor_shift_x = 16.0 - float(d.car_sprite_anchor_x)
        anchor_shift_back = 16.0 - float(d.car_sprite_anchor_y)
        wheel_dx = float(d.fx_dust_wheel_dx_px) + anchor_shift_x
        back = float(d.fx_dust_back_px) + anchor_shift_back
        jitter_x = float(d.fx_dust_jitter_x_px)
        jitter_y = float(d.fx_dust_jitter_y_px)

        i = 0
        while i < n:
            jx = (self._rng.rand01() - 0.5) * jitter_x
            jy = (self._rng.rand01()) * jitter_y

            x_l = (self._cx - wheel_dx) + jx
            y_l = (self._cy + back) + jy
            x_r = (self._cx + wheel_dx) - jx
            y_r = (self._cy + back) + jy

            r = self._rng.rand01() * 8.0
            self._v.spawn_dust_down(x_l, y_l, r)
            self._v.spawn_dust_down(x_r, y_r, r)
            i += 1

    def draw(self) -> None:
        self._v.draw()


class _TimedPslibFx(FxSystem):
    """Оборачивает `PslibFx` и принудительно останавливает эмиссию по таймеру."""

    def __init__(self, fx: PslibFx, emit_seconds: float) -> None:
        self._fx = fx
        self._emit_left = emit_seconds
        self._stopped = False

    def alive(self) -> bool:
        return self._fx.alive()

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        if not self._stopped:
            self._emit_left -= dt
            if self._emit_left <= 0.0:
                self._stop_emission()
        self._fx.update(dt, world_dx, world_dy)

    def draw(self) -> None:
        self._fx.draw()

    def _stop_emission(self) -> None:
        i = 0
        while i < len(self._fx._systems):
            ps = self._fx._systems[i]
            ps.emittimers = []
            ps.autoremove = True
            i += 1
        self._stopped = True


def drive_fx_register_defaults(fx: DriveFx) -> None:
    """Регистрирует стандартные фабрики стартовых и ударных FX."""
    fx._start_reg.register(
        FxId.DRIVE_START_DUST_CURRENT,
        fx._make_start_dust_current,
        "start: dust (current)"
    )
    fx._start_reg.register(
        FxId.DRIVE_START_SMOKE_PSLIB,
        fx._make_start_smoke_pslib,
        "start: smoke (pslib)"
    )
    fx._start_reg.register(
        FxId.DRIVE_START_SMOKE_VAND_DUST,
        fx._make_start_smoke_vand_dust,
        "start: smoke (vand dust)"
    )
    fx._hit_reg.register(
        FxId.DRIVE_HIT_SPARKS_CURRENT,
        fx._make_hit_sparks_current,
        "hit: sparks (current)"
    )
    fx._hit_reg.register(
        FxId.DRIVE_HIT_EXPLOSION_PSLIB,
        fx._make_hit_explosion_pslib,
        "hit: explosion (pslib)"
    )
    fx._hit_reg.register(
        FxId.DRIVE_HIT_VAND_EXPLOSION,
        fx._make_hit_explosion_vand,
        "hit: explosion (vand)"
    )
    fx._hit_reg.register(
        FxId.DRIVE_HIT_EXPLOSION_PSLIB_PLUS_SPARKS,
        fx._make_hit_explosion_pslib,
        "hit: explosion+sparks (pslib+current)"
    )
    fx._hit_reg.register(
        FxId.DRIVE_HIT_VAND_EXPLOSION_PLUS_SPARKS,
        fx._make_hit_explosion_vand,
        "hit: explosion+sparks (vand+current)"
    )


def drive_fx_make_start_dust_current(fx: DriveFx, p: _FxStartParams) -> FxSystem:
    """Создаёт стартовый `Particles2D`-дым из текущего тюнинга."""
    d = fx._tuning.DRIVE
    rng = Rng(int(p.seed))
    particles = Particles2D(int(d.fx_particles_max))
    return _StartDustFx(d, rng, particles, float(p.cx), float(p.cy), float(p.seconds))


def drive_fx_make_start_smoke_pslib(fx: DriveFx, p: _FxStartParams) -> FxSystem:
    """Создаёт стартовый дым на пресете `pslib` с перекраской в бело-серую гамму."""
    d = fx._tuning.DRIVE
    wheel_dx = float(d.fx_dust_wheel_dx_px)
    back = float(d.fx_dust_back_px)

    rng_l = Rng(int(p.seed))
    rng_r = Rng(int(p.seed) ^ 0x9E3779B9)
    y = float(p.cy + back)
    sx_l = float(p.cx - wheel_dx)
    sx_r = float(p.cx + wheel_dx)

    a = make_smoke_fx(rng_l, sx_l, y)
    b = make_smoke_fx(rng_r, sx_r, y)

    colors = [Color.WHITE, Color.LIGHT_GREY, Color.GREY, Color.DARK_GREY]
    smoke_list = [a, b]
    si = 0
    while si < len(smoke_list):
        smoke_fx = smoke_list[si]
        j = 0
        while j < len(smoke_fx._systems):
            ps = smoke_fx._systems[j]
            k = 0
            while k < len(ps.drawfuncs):
                df = ps.drawfuncs[k]
                if getattr(df.params, "colors", None) is not None:
                    df.params.colors = colors
                k += 1
            j += 1
        si += 1

    combo = PslibFx()
    combo._systems.extend(a._systems)
    combo._systems.extend(b._systems)
    return _TimedPslibFx(combo, float(p.seconds))


def drive_fx_make_start_smoke_vand_dust(fx: DriveFx, p: _FxStartParams) -> FxSystem:
    """Создаёт стартовый дым через `VandParticles` (две точки эмиссии колёс)."""
    d = fx._tuning.DRIVE
    v = VandParticles(int(p.seed))
    rng = Rng(int(p.seed) ^ 0xA5A5A5A5)
    return _StartVandDustFx(d, v, rng, float(p.cx), float(p.cy), float(p.seconds))


def drive_fx_make_hit_sparks_current(fx: DriveFx, p: _FxHitParams) -> FxSystem:
    """Создаёт текущий burst искр удара (`Particles2D`)."""
    d = fx._tuning.DRIVE
    rng = Rng(int(p.seed))
    particles = Particles2D(max(16, int(d.fx_particles_max / 2)))

    sx, sy = p.proj.world_to_screen(p.wx, p.wy)
    vx, vy = p.proj.world_vec_to_screen(-p.nx, -p.ny)
    l2 = vx * vx + vy * vy
    if l2 > 0.0:
        inv = 1.0 / (l2 ** 0.5)
        vx *= inv
        vy *= inv
    else:
        vx = 0.0
        vy = 1.0

    off = p.hit_r + 2.0
    x0 = float(sx - vx * off)
    y0 = float(sy - vy * off)

    impact = float(p.impact)
    n = 3 + int(impact * 0.10)
    if n > 18:
        n = 18
    speed = 120.0 + impact * 1.2
    if speed > 260.0:
        speed = 260.0
    life = 10 + int(impact * 0.08)
    if life > 22:
        life = 22

    perp_x = -vy
    perp_y = vx
    i = 0
    while i < n:
        t0 = rng.rand01()
        t1 = rng.rand01()
        t2 = rng.rand01()

        spread = 0.75 + impact / 120.0
        if spread > 1.35:
            spread = 1.35
        if spread < 0.25:
            spread = 0.25
        j_perp = (t0 - 0.5) * spread
        out_x = vx + perp_x * j_perp
        out_y = vy + perp_y * j_perp
        ol2 = out_x * out_x + out_y * out_y
        if ol2 > 0.0:
            inv = 1.0 / (ol2 ** 0.5)
            out_x *= inv
            out_y *= inv

        jx = (t1 - 0.5) * 3.0
        jy = (t2 - 0.5) * 3.0

        sp = speed * (0.80 + 0.40 * t2)
        pvx = out_x * sp
        pvy = out_y * sp

        seg = 2.0 + t1 * 4.0
        dx = out_x * seg
        dy = out_y * seg

        m = int(rng.next_u32() % 3)
        color = Color.WHITE
        if m == 1:
            color = Color.YELLOW
        elif m == 2:
            color = Color.ORANGE

        particles.spawn(x0 + jx, y0 + jy, dx, dy, pvx, pvy, life, color)
        i += 1

    return _Particles2DFx(particles)


def drive_fx_make_hit_explosion_pslib(_fx: DriveFx, p: _FxHitParams) -> FxSystem:
    """Создаёт pslib-взрыв в точке контакта."""
    rng = Rng(int(p.seed))
    sx, sy = p.proj.world_to_screen(p.wx, p.wy)
    return make_explosion_fx(rng, float(sx), float(sy))


def drive_fx_make_hit_explosion_vand(_fx: DriveFx, p: _FxHitParams) -> FxSystem:
    """Создаёт компактный `VandParticles`-взрыв, ориентированный по -normal."""
    sx, sy = p.proj.world_to_screen(p.wx, p.wy)
    v = VandParticles(int(p.seed))
    r = 3.0 + float(p.impact) * 0.03
    if r > 8.0:
        r = 8.0

    dir_x, dir_y = p.proj.world_vec_to_screen(-p.nx, -p.ny)
    l2 = dir_x * dir_x + dir_y * dir_y
    if l2 > 0.0:
        inv = 1.0 / (l2 ** 0.5)
        dir_x *= inv
        dir_y *= inv
    else:
        dir_x = 0.0
        dir_y = -1.0
    v.spawn_explosion_dir(float(sx), float(sy), r, float(dir_x), float(dir_y))
    return v
