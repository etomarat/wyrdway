from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from ...contracts import DriveTuning, Tuning
    from ...core.palette import Color
    from ..fx.fx_ids import FxId
    from ..fx.fx_manager import FxLayer, FxManager, FxSystem
    from ..fx.vendor.vand_particles import VandParticles
    from ..fx.vendor.viza_presets import make_explosion_fx, make_smoke_fx
    from ..fx.vendor.viza_pslib import PslibFx
    from .fx_particles import Particles2D
    from .rng import Rng


class DriveFxProjector:
    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        return (0.0, 0.0)

    def world_vec_to_screen(self, vx: float, vy: float) -> tuple[float, float]:
        return (0.0, 0.0)


class TopdownProjector(DriveFxProjector):
    def __init__(
        self,
        cam_x: float,
        cam_y: float,
        cam_fwd_x: float,
        cam_fwd_y: float,
        center_x: int,
        center_y: int
    ) -> None:
        self._cam_x = cam_x
        self._cam_y = cam_y
        self._fwd_x = cam_fwd_x
        self._fwd_y = cam_fwd_y
        self._right_x = -cam_fwd_y
        self._right_y = cam_fwd_x
        self._cx = center_x
        self._cy = center_y

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        vx = wx - self._cam_x
        vy = wy - self._cam_y
        local_fwd = vx * self._fwd_x + vy * self._fwd_y
        local_right = vx * self._right_x + vy * self._right_y
        sx = self._cx + local_right
        sy = self._cy - local_fwd
        return (sx, sy)

    def world_vec_to_screen(self, vx: float, vy: float) -> tuple[float, float]:
        local_fwd = vx * self._fwd_x + vy * self._fwd_y
        local_right = vx * self._right_x + vy * self._right_y
        sx = local_right
        sy = -local_fwd
        return (sx, sy)


class _FxStartParams:
    def __init__(self, cx: float, cy: float, seed: int, seconds: float) -> None:
        self.cx = cx
        self.cy = cy
        self.seed = seed
        self.seconds = seconds


class _FxHitParams:
    def __init__(
        self,
        wx: float,
        wy: float,
        nx: float,
        ny: float,
        impact: float,
        seed: int,
        hit_r: float,
        proj: DriveFxProjector
    ) -> None:
        self.wx = wx
        self.wy = wy
        self.nx = nx
        self.ny = ny
        self.impact = impact
        self.seed = seed
        self.hit_r = hit_r
        self.proj = proj


class _Particles2DFx(FxSystem):
    def __init__(self, p: Particles2D) -> None:
        self._p = p

    def alive(self) -> bool:
        return self._p.count() > 0

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        self._p.update(dt, world_dx, world_dy)

    def draw(self) -> None:
        self._p.draw()


class _StartDustFx(FxSystem):
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

        # Плотность дыма берём из того же тюнинга, что и стартовая пыль.
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
            # vand pack demo (#5) спавнит несколько dust частиц; здесь делаем “дым из колёс”
            # как 2 источника (лев/прав) + небольшой шум.
            jx = (self._rng.rand01() - 0.5) * jitter_x
            jy = (self._rng.rand01()) * jitter_y

            x_l = (self._cx - wheel_dx) + jx
            y_l = (self._cy + back) + jy
            x_r = (self._cx + wheel_dx) - jx
            y_r = (self._cy + back) + jy

            # В оригинале радиус = rnd()*8.
            r = self._rng.rand01() * 8.0
            self._v.spawn_dust_down(x_l, y_l, r)
            self._v.spawn_dust_down(x_r, y_r, r)
            i += 1

    def draw(self) -> None:
        self._v.draw()


class _TimedPslibFx(FxSystem):
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
        # Останавливаем emit timers, чтобы система стала конечной.
        i = 0
        while i < len(self._fx._systems):
            ps = self._fx._systems[i]
            ps.emittimers = []
            ps.autoremove = True
            i += 1
        self._stopped = True


class DriveFx:
    def __init__(self, tuning: "Tuning") -> None:
        self._tuning = tuning
        self._mgr = FxManager()
        self._start_factories: dict[int, Callable[[_FxStartParams], FxSystem]] = {}
        self._hit_factories: dict[int, Callable[[_FxHitParams], FxSystem]] = {}
        self._register_defaults()

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        self._mgr.update(dt, world_dx, world_dy)

    def draw(self, layer: int) -> None:
        self._mgr.draw(layer)

    def start_move(self, cx: int, cy: int, seed: int) -> None:
        d = self._tuning.DRIVE
        fx_id = int(d.fx_start_id)
        params = _FxStartParams(float(cx), float(
            cy), seed, float(d.fx_start_dust_seconds))
        fx = self._spawn_start_fx(fx_id, params)
        if fx is not None:
            self._mgr.add(FxLayer.UNDER_CAR, fx)

    def obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        seed: int,
        hit_r: float,
        proj: DriveFxProjector
    ) -> None:
        d = self._tuning.DRIVE
        fx_id = int(d.fx_hit_id)
        if fx_id == FxId.DRIVE_HIT_EXPLOSION_PSLIB_PLUS_SPARKS:
            params = _FxHitParams(contact_wx, contact_wy,
                                  normal_x, normal_y, impact, seed, hit_r, proj)
            a = self._spawn_hit_fx(FxId.DRIVE_HIT_EXPLOSION_PSLIB, params)
            b = self._spawn_hit_fx(FxId.DRIVE_HIT_SPARKS_CURRENT, params)
            if a is not None:
                self._mgr.add(FxLayer.OVER_CAR, a)
            if b is not None:
                self._mgr.add(FxLayer.OVER_CAR, b)
            return
        if fx_id == FxId.DRIVE_HIT_VAND_EXPLOSION_PLUS_SPARKS:
            params = _FxHitParams(contact_wx, contact_wy,
                                  normal_x, normal_y, impact, seed, hit_r, proj)
            sparks = self._spawn_hit_fx(FxId.DRIVE_HIT_SPARKS_CURRENT, params)
            expl = self._spawn_hit_fx(FxId.DRIVE_HIT_VAND_EXPLOSION, params)
            if sparks is not None:
                self._mgr.add(FxLayer.OVER_CAR, sparks)
            if expl is not None:
                self._mgr.add(FxLayer.OVER_CAR, expl)
            return

        params = _FxHitParams(contact_wx, contact_wy,
                              normal_x, normal_y, impact, seed, hit_r, proj)
        fx = self._spawn_hit_fx(fx_id, params)
        if fx is not None:
            self._mgr.add(FxLayer.OVER_CAR, fx)

    def _register_defaults(self) -> None:
        self._register_start_fx(FxId.DRIVE_START_DUST_CURRENT, self._make_start_dust_current)
        self._register_start_fx(FxId.DRIVE_START_SMOKE_PSLIB, self._make_start_smoke_pslib)
        self._register_start_fx(FxId.DRIVE_START_SMOKE_VAND_DUST, self._make_start_smoke_vand_dust)
        self._register_hit_fx(FxId.DRIVE_HIT_SPARKS_CURRENT, self._make_hit_sparks_current)
        self._register_hit_fx(FxId.DRIVE_HIT_EXPLOSION_PSLIB, self._make_hit_explosion_pslib)
        self._register_hit_fx(FxId.DRIVE_HIT_VAND_EXPLOSION, self._make_hit_explosion_vand)
        self._register_hit_fx(
            FxId.DRIVE_HIT_EXPLOSION_PSLIB_PLUS_SPARKS,
            self._make_hit_explosion_pslib
        )
        self._register_hit_fx(
            FxId.DRIVE_HIT_VAND_EXPLOSION_PLUS_SPARKS,
            self._make_hit_explosion_vand
        )

    def _register_start_fx(self, fx_id: int, factory: Callable[[_FxStartParams], FxSystem]) -> None:
        self._start_factories[fx_id] = factory

    def _register_hit_fx(self, fx_id: int, factory: Callable[[_FxHitParams], FxSystem]) -> None:
        self._hit_factories[fx_id] = factory

    def _spawn_start_fx(self, fx_id: int, params: _FxStartParams) -> FxSystem | None:
        f = self._start_factories.get(fx_id)
        if f is None:
            return None
        return f(params)

    def _spawn_hit_fx(self, fx_id: int, params: _FxHitParams) -> FxSystem | None:
        f = self._hit_factories.get(fx_id)
        if f is None:
            return None
        return f(params)

    def _make_start_dust_current(self, p: _FxStartParams) -> FxSystem:
        d = self._tuning.DRIVE
        rng = Rng(int(p.seed))
        fx = Particles2D(int(d.fx_particles_max))
        return _StartDustFx(d, rng, fx, float(p.cx), float(p.cy), float(p.seconds))

    def _make_start_smoke_pslib(self, p: _FxStartParams) -> FxSystem:
        d = self._tuning.DRIVE
        wheel_dx = float(d.fx_dust_wheel_dx_px)
        back = float(d.fx_dust_back_px)

        # Дым из-под задних колёс: 2 источника, бело-серая гамма.
        # В демо это было как "smoke" из pslib, но в нашей палитре делаем именно белым.
        rng_l = Rng(int(p.seed))
        rng_r = Rng(int(p.seed) ^ 0x9E3779B9)
        y = float(p.cy + back)
        sx_l = float(p.cx - wheel_dx)
        sx_r = float(p.cx + wheel_dx)

        a = make_smoke_fx(rng_l, sx_l, y)
        b = make_smoke_fx(rng_r, sx_r, y)

        # Перекрашиваем smoke в бело-серую гамму (в оригинальном демо были другие цвета).
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

        # Smoke preset is continuous, so we stop emission after `seconds`.
        return _TimedPslibFx(combo, float(p.seconds))

    def _make_start_smoke_vand_dust(self, p: _FxStartParams) -> FxSystem:
        d = self._tuning.DRIVE
        v = VandParticles(int(p.seed))
        rng = Rng(int(p.seed) ^ 0xA5A5A5A5)
        return _StartVandDustFx(d, v, rng, float(p.cx), float(p.cy), float(p.seconds))

    def _make_hit_sparks_current(self, p: _FxHitParams) -> FxSystem:
        d = self._tuning.DRIVE
        rng = Rng(int(p.seed))
        fx = Particles2D(max(16, int(d.fx_particles_max / 2)))

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
        # Искры хотим чуть "со стороны машины" (под взрывом), но лететь они могут по -normal.
        x0 = float(sx - vx * off)
        y0 = float(sy - vy * off)

        # Reuse colors from palette: white/yellow/orange.
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

            fx.spawn(x0 + jx, y0 + jy, dx, dy, pvx, pvy, life, color)
            i += 1

        return _Particles2DFx(fx)

    def _make_hit_explosion_pslib(self, p: _FxHitParams) -> FxSystem:
        rng = Rng(int(p.seed))
        sx, sy = p.proj.world_to_screen(p.wx, p.wy)
        expl = make_explosion_fx(rng, float(sx), float(sy))
        return expl

    def _make_hit_explosion_vand(self, p: _FxHitParams) -> FxSystem:
        sx, sy = p.proj.world_to_screen(p.wx, p.wy)
        v = VandParticles(int(p.seed))
        # В оригинальном демо (#4) радиус был rnd()*8. Здесь делаем мягкую зависимость от impact,
        # но держим эффект компактным.
        r = 3.0 + float(p.impact) * 0.03
        if r > 8.0:
            r = 8.0

        # Вандовский взрыв из демо направлен "вверх". Для DRIVE направляем его по -normal,
        # чтобы он "вылетал" в сторону движения при лобовом ударе.
        dir_x, dir_y = p.proj.world_vec_to_screen(-p.nx, -p.ny)
        l2 = dir_x * dir_x + dir_y * dir_y
        if l2 > 0.0:
            inv = 1.0 / (l2 ** 0.5)
            dir_x *= inv
            dir_y *= inv
        else:
            dir_x = 0.0
            dir_y = -1.0
        v.spawn_explosion_dir(float(sx), float(
            sy), r, float(dir_x), float(dir_y))
        return v
