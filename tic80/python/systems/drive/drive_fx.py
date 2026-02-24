from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning
    from ..fx.fx_ids import FxId
    from ..fx.fx_manager import FxLayer, FxManager, FxSystem
    from ..fx.fx_registry import FxRegistry
    from .drive_fx_factories import (
        drive_fx_make_hit_explosion_pslib,
        drive_fx_make_hit_explosion_vand,
        drive_fx_make_hit_sparks_current,
        drive_fx_make_start_dust_current,
        drive_fx_make_start_smoke_pslib,
        drive_fx_make_start_smoke_vand_dust,
        drive_fx_register_defaults
    )


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


class DriveFx:
    def __init__(self, tuning: "Tuning") -> None:
        self._tuning = tuning
        self._mgr = FxManager()
        self._start_reg = FxRegistry[_FxStartParams]()
        self._hit_reg = FxRegistry[_FxHitParams]()
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
        fx = self._start_reg.spawn(fx_id, params)
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
            a = self._hit_reg.spawn(FxId.DRIVE_HIT_EXPLOSION_PSLIB, params)
            b = self._hit_reg.spawn(FxId.DRIVE_HIT_SPARKS_CURRENT, params)
            if a is not None:
                self._mgr.add(FxLayer.OVER_CAR, a)
            if b is not None:
                self._mgr.add(FxLayer.OVER_CAR, b)
            return
        if fx_id == FxId.DRIVE_HIT_VAND_EXPLOSION_PLUS_SPARKS:
            params = _FxHitParams(contact_wx, contact_wy,
                                  normal_x, normal_y, impact, seed, hit_r, proj)
            sparks = self._hit_reg.spawn(FxId.DRIVE_HIT_SPARKS_CURRENT, params)
            expl = self._hit_reg.spawn(FxId.DRIVE_HIT_VAND_EXPLOSION, params)
            if sparks is not None:
                self._mgr.add(FxLayer.OVER_CAR, sparks)
            if expl is not None:
                self._mgr.add(FxLayer.OVER_CAR, expl)
            return

        params = _FxHitParams(contact_wx, contact_wy,
                              normal_x, normal_y, impact, seed, hit_r, proj)
        fx = self._hit_reg.spawn(fx_id, params)
        if fx is not None:
            self._mgr.add(FxLayer.OVER_CAR, fx)

    def _register_defaults(self) -> None:
        drive_fx_register_defaults(self)

    def _make_start_dust_current(self, p: _FxStartParams) -> FxSystem:
        return drive_fx_make_start_dust_current(self, p)

    def _make_start_smoke_pslib(self, p: _FxStartParams) -> FxSystem:
        return drive_fx_make_start_smoke_pslib(self, p)

    def _make_start_smoke_vand_dust(self, p: _FxStartParams) -> FxSystem:
        return drive_fx_make_start_smoke_vand_dust(self, p)

    def _make_hit_sparks_current(self, p: _FxHitParams) -> FxSystem:
        return drive_fx_make_hit_sparks_current(self, p)

    def _make_hit_explosion_pslib(self, p: _FxHitParams) -> FxSystem:
        return drive_fx_make_hit_explosion_pslib(self, p)

    def _make_hit_explosion_vand(self, p: _FxHitParams) -> FxSystem:
        return drive_fx_make_hit_explosion_vand(self, p)
