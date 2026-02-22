import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, circb, line, print, ttri

    from ...contracts import PursuerVariantTuning
    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.drive_objects import DriveObjects, DriveZone
    from ...systems.drive.drive_screen_shake import DriveScreenShake
    from ...systems.drive.pursuers.archetypes import PursuerArchetype
    from ...systems.drive.rng import lcg_next_u32
    from ...systems.drive.road_model import RoadModel
    from .car_pose2d import CarPose2D
    from .topdown_debug_draw import TopdownDebugDraw
    from .topdown_fx_overlay import TopdownFxOverlay
    from .topdown_obstacles_draw import TopdownObstaclesDraw
    from .topdown_road_draw import TopdownRoadDraw
    from .topdown_skid_marks import TopdownSkidMarks


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    _CAR_SPRITE_BASE_ID = 256
    _CAR_CHROMAKEY = 12
    # Crop empty right column (8px) from repacked #256 block.
    _CAR_SRC_X0 = 0.0
    _CAR_SRC_Y0 = 0.0
    _CAR_SRC_X1 = 24.0
    _CAR_SRC_Y1 = 32.0
    _PRIME_WORDS = [
        "void",
        "def",
        "class",
        "struct",
        "typedef",
        "enum",
        "union",
        "static",
        "extern",
        "const",
        "volatile",
        "return",
        "sizeof",
        "NULL",
        "malloc",
        "free",
        "import",
        "lambda",
        "async",
        "await",
        "protocol",
        "module",
        "sentinel",
        "oracle"
    ]
    _ENTITY_WORDS = [
        "0x00",
        "0x1F",
        "0x2A",
        "0x3C",
        "0x7E",
        "0xA0",
        "0xB7",
        "0xFF",
        "jmp",
        "mov",
        "xor",
        "and",
        "or",
        "shl",
        "shr",
        "irq",
        "nmi",
        "ptr",
        "reg",
        "eax",
        "rsp",
        "seg",
        "addr",
        "bus"
    ]
    _ENTITY_ERRORS = [
        "SIGSEGV",
        "SEGFAULT",
        # "PAGE FAULT",
        # "BUS ERROR",
        "ILLEGAL OPCODE",
        "STACK SMASH",
        "NULL PTR",
        "BAD ADDR",
        "IRQ LOST",
        "TRAP 0x0D",
        "RING VIOLATION",
        # "MMU FAULT"
    ]
    _PRIME_ERRORS = [
        "ACCESS VIOLATION",
        "UNHANDLED EXCEPTION",
        "HEAP CORRUPTION",
        "STACK OVERFLOW",
        "INTEGRITY FAILURE",
        "FORBIDDEN CALL",
        "STATE CORRUPTED",
        "THREAD DEADLOCK",
        "WATCHDOG TIMEOUT",
        "SYSTEM HALTED",
        "MEMORY POISONED",
        "PANIC: NO RETURN"
    ]
    # Internal compensation for atlas repack: old 32x32 sprite had 8px empty left column.
    # Not gameplay tuning; keeps existing anchor-aligned geometry unchanged.
    _CAR_SOURCE_REPACK_SHIFT_X = 8.0
    def __init__(self) -> None:
        self._road_draw = TopdownRoadDraw()
        self._obstacles_draw = TopdownObstaclesDraw()
        self._skid_marks = TopdownSkidMarks()
        self._debug_draw = TopdownDebugDraw()
        self._fx_overlay = TopdownFxOverlay()
        self._shake = DriveScreenShake()
        self._cam_fwd_x = 1.0
        self._cam_fwd_y = 0.0
        self._cam_inited = False
        self._cam_angle = 0.0
        self._cam_ang_vel = 0.0
        self._cam_vel_x = 1.0
        self._cam_vel_y = 0.0
        self._pursuer_anim_t = 0.0
        self._pursuer_draw_s = 0.0
        self._pursuer_draw_inited = False
        self._pursuer_screen_x = 0.0
        self._pursuer_screen_y = 0.0
        self._pursuer_screen_inited = False
        self._pursuer_intro_active = False
        self._pursuer_intro_t = 0.0
        self._pursuer_intro_start_x = 0.0
        self._pursuer_intro_start_y = 0.0
        self._pursuer_error_text = ""
        self._pursuer_error_t = 0.0
        self._pursuer_error_color = Color.RED
        self._pursuer_error_seed = 0x13579BDF

    def notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        hitbox_radius: float
    ) -> None:
        self._fx_overlay.notify_obstacle_hit(
            contact_wx,
            contact_wy,
            normal_x,
            normal_y,
            impact,
            hitbox_radius
        )
        self._shake.notify_hit(impact, TUNING)

    def notify_pursuer_strike(self, intensity: float, variant_id: str) -> None:
        if intensity <= 0.0:
            return
        self._shake.notify_hit(float(intensity), TUNING)
        self._queue_pursuer_error_text(str(variant_id))

    def notify_pursuer_hp_strike_fx(
        self,
        logic: DriveLogic,
        hp_loss: int,
        strike_shake_intensity: float
    ) -> None:
        if hp_loss <= 0:
            return
        rear_x, rear_y, rear_r, front_x, front_y, front_r = logic.hitbox_world_circles()
        if rear_r <= 0.0 and front_r <= 0.0:
            return

        # Спавним FX в фактической точке удара (задний хитбокс машины).
        fwd_x = float(logic.fwd_x)
        fwd_y = float(logic.fwd_y)
        hit_r = rear_r
        if hit_r <= 0.0:
            hit_r = 4.0

        impact = float(strike_shake_intensity) * 1.8 + float(hp_loss) * 12.0
        if impact < 36.0:
            impact = 36.0
        if impact > 120.0:
            impact = 120.0

        # Разворачиваем нормаль так, чтобы вылет искр читался "внутрь машины".
        nx = -fwd_x
        ny = -fwd_y
        self._fx_overlay.notify_obstacle_hit(
            rear_x,
            rear_y,
            nx,
            ny,
            impact,
            hit_r
        )

    def draw(
        self,
        road: RoadModel,
        logic: DriveLogic,
        objects: DriveObjects,
        active_zone: DriveZone | None,
        pursuer_archetype: PursuerArchetype | None = None,
        pursuer_state: str | None = None,
        pursuer_s: float = 0.0,
        strike_flash: float = 0.0,
        screen_glitch_active: bool = False
    ) -> None:
        self._shake.ensure_seed(road.seed)
        self._pursuer_anim_t += float(TUNING.CORE.dt)
        if self._pursuer_error_t > 0.0:
            self._pursuer_error_t -= float(TUNING.CORE.dt)
            if self._pursuer_error_t <= 0.0:
                self._pursuer_error_t = 0.0
                self._pursuer_error_text = ""
        shake_x, shake_y = self._shake.update(
            float(TUNING.CORE.dt),
            logic.offroad,
            self._fx_overlay.exhaust_strength(),
            TUNING
        )

        center_x = 120 + self._round_to_int(shake_x)
        center_y = self._road_draw.clamp_center_y(int(TUNING.DRIVE.view_center_y))
        center_y += self._round_to_int(shake_y)

        p_s = logic.road_s
        car_x = logic.x
        car_y = logic.y
        cam_fwd_x, cam_fwd_y = self._camera_forward(logic)
        proj = TopdownProjector(car_x, car_y, cam_fwd_x, cam_fwd_y, center_x, center_y)
        pose = CarPose2D(logic, proj, center_x, center_y)

        start_idx, end_idx = self._road_draw.visible_index_range(road, p_s)
        zones = objects.zones_items()
        self._road_draw.draw_road_edges_and_zones(
            road,
            zones,
            start_idx,
            end_idx,
            proj
        )

        if TUNING.DRIVE.debug_zones_enabled:
            i = 0
            while i < len(zones):
                z = zones[i]
                color = Color.GREEN
                if active_zone is not None and z is active_zone:
                    color = Color.WHITE
                self._road_draw.draw_zone_outline(
                    road,
                    z,
                    start_idx,
                    end_idx,
                    proj,
                    color
                )
                i += 1

        obstacles = objects.obstacles_items()
        self._obstacles_draw.draw(
            obstacles,
            road,
            p_s,
            proj
        )

        # FX/следы лучше рисовать ДО машины, чтобы кузов перекрывал их.
        start_move = self._fx_overlay.update(road, logic, proj, pose)
        if start_move:
            self._skid_marks.trigger_start(float(TUNING.DRIVE.start_skid_seconds))
        self._skid_marks.update_and_draw(logic, proj, pose)

        # Следы шин должны быть ПОД пылью/дымом.
        self._fx_overlay.draw_world()

        # Стартовый дым/пыль рисуем ВЫШЕ skid marks, но НИЖЕ кузова.
        self._fx_overlay.draw_under_car()
        self._draw_car_ttri(pose)
        self._fx_overlay.draw_over_car()
        # Преследователь рисуем ПОСЛЕ машины, чтобы он всегда был поверх кузова.
        self._draw_pursuer_world(
            road,
            proj,
            logic,
            pose,
            pursuer_archetype,
            pursuer_state,
            pursuer_s,
            strike_flash,
            screen_glitch_active
        )

        if TUNING.DRIVE.debug_vectors_enabled:
            self._debug_draw.draw_vectors(logic, proj, center_x, center_y)
        if TUNING.DRIVE.debug_hitboxes_enabled:
            self._debug_draw.draw_hitboxes(logic, proj)
            if pursuer_archetype is not None:
                profile = pursuer_archetype.profile
                self._debug_draw.draw_pursuer_strike_range(
                    road,
                    proj,
                    float(logic.road_s),
                    float(profile.strike_begin_dist_s)
                )

    def _draw_pursuer_world(
        self,
        road: RoadModel,
        proj: TopdownProjector,
        logic: DriveLogic,
        pose: CarPose2D,
        pursuer_archetype: PursuerArchetype | None,
        pursuer_state: str | None,
        pursuer_s: float,
        strike_flash: float,
        screen_glitch_active: bool
    ) -> None:
        if pursuer_state is None or pursuer_state == "FAR" or pursuer_archetype is None:
            self._pursuer_draw_inited = False
            self._pursuer_screen_inited = False
            self._pursuer_intro_active = False
            self._pursuer_intro_t = 0.0
            return

        profile = pursuer_archetype.profile
        contact_s = float(pursuer_s)
        if contact_s < 0.0:
            contact_s = 0.0
        if contact_s > road.segment_total_length:
            contact_s = road.segment_total_length
        s = contact_s
        visual_offset = float(profile.contact_offset_s)
        if visual_offset > 0.0:
            s -= visual_offset
        if s < 0.0:
            s = 0.0
        if s > road.segment_total_length:
            s = road.segment_total_length

        if (not self._pursuer_draw_inited) or abs(s - self._pursuer_draw_s) > 48.0:
            self._pursuer_draw_s = s
            self._pursuer_draw_inited = True
        else:
            # Сглаживаем позицию преследователя на экране, чтобы убрать дёрганье
            # из-за мелких колебаний centerline/camera.
            lerp = 0.14
            self._pursuer_draw_s += (s - self._pursuer_draw_s) * lerp

        draw_s = self._pursuer_draw_s
        cx, cy = road.sample_centerline(draw_s)
        dir_x, dir_y = road.direction_at(draw_s)
        right_x = -dir_y
        right_y = dir_x
        t = self._pursuer_anim_t
        wobble = 1.4
        if pursuer_state == "NEAR":
            wobble = 2.2
        phase = float(road.seed & 1023) * 0.01
        wobble *= (
            0.60 * math.sin(t * 4.5 + phase + self._cam_angle * 1.6)
            + 0.40 * math.sin(t * 2.7 + phase * 1.3)
        )
        wx = cx + right_x * wobble
        wy = cy + right_y * wobble
        sx, sy = proj.world_to_screen(wx, wy)

        if not self._pursuer_screen_inited:
            entry_y = float(profile.intro_entry_screen_y)
            if entry_y <= 0.0:
                entry_y = 164.0
            self._pursuer_screen_x = sx
            self._pursuer_screen_y = entry_y
            self._pursuer_screen_inited = True
            self._pursuer_intro_active = True
            self._pursuer_intro_t = 0.0
            self._pursuer_intro_start_x = sx
            self._pursuer_intro_start_y = entry_y
        elif (abs(sx - self._pursuer_screen_x) + abs(sy - self._pursuer_screen_y) > 80.0) and (not self._pursuer_intro_active):
            self._pursuer_screen_x = sx
            self._pursuer_screen_y = sy

        if self._pursuer_intro_active:
            self._pursuer_intro_t += float(TUNING.CORE.dt)
            n = 1.0
            entry_seconds = float(profile.intro_entry_seconds)
            if entry_seconds <= 0.0:
                entry_seconds = 0.75
            if entry_seconds > 0.0001:
                n = self._pursuer_intro_t / entry_seconds
            if n < 0.0:
                n = 0.0
            if n > 1.0:
                n = 1.0
            ease = n * n * (3.0 - 2.0 * n)
            self._pursuer_screen_x = (
                self._pursuer_intro_start_x
                + (sx - self._pursuer_intro_start_x) * ease
            )
            self._pursuer_screen_y = (
                self._pursuer_intro_start_y
                + (sy - self._pursuer_intro_start_y) * ease
            )
            if n >= 1.0:
                self._pursuer_intro_active = False
        else:
            screen_lerp = 0.14
            if pursuer_state == "NEAR":
                screen_lerp = 0.09
            self._pursuer_screen_x += (sx - self._pursuer_screen_x) * screen_lerp
            self._pursuer_screen_y += (sy - self._pursuer_screen_y) * screen_lerp

        px = int(self._pursuer_screen_x)
        py = int(self._pursuer_screen_y)

        seed_base = (
            road.seed
            ^ int(draw_s * 17.0)
            ^ int(self._pursuer_anim_t * 1000.0)
        ) & 0xFFFFFFFF
        half_w = road.width_at(draw_s) * 0.5
        rx, ry = proj.world_to_screen(
            cx + right_x * half_w,
            cy + right_y * half_w
        )
        road_half_px = ((rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)) ** 0.5
        pursuer_archetype.draw_body(
            self,
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px
        )
        self._draw_pursuer_error_overlay(screen_glitch_active)
        if profile.debug_contact_marker:
            # TEMP: яркая метка в логической контактной точке (до visual contact_offset_s).
            # Нужна для настройки offset относительно тела преследователя.
            ccx, ccy = road.sample_centerline(contact_s)
            cdir_x, cdir_y = road.direction_at(contact_s)
            crx = -cdir_y
            cry = cdir_x
            cwobble = 1.4
            if pursuer_state == "NEAR":
                cwobble = 2.2
            cwobble *= (
                0.60 * math.sin(t * 4.5 + phase + self._cam_angle * 1.6)
                + 0.40 * math.sin(t * 2.7 + phase * 1.3)
            )
            csx, csy = proj.world_to_screen(
                ccx + crx * cwobble,
                ccy + cry * cwobble
            )
            circ(int(csx), int(csy), 2, Color.WHITE)
            circb(int(csx), int(csy), 3, Color.RED)

        rear_x, rear_y, _, _, _, _ = logic.hitbox_world_circles()
        hit_sx, hit_sy = proj.world_to_screen(rear_x, rear_y)
        if strike_flash > 0.0:
            flash_dur = float(profile.strike_flash_seconds)
            flash_n = 1.0
            if flash_dur > 0.0001:
                flash_n = strike_flash / flash_dur
            if flash_n < 0.0:
                flash_n = 0.0
            if flash_n > 1.0:
                flash_n = 1.0
            pursuer_archetype.draw_strike(
                self,
                px,
                py,
                int(hit_sx),
                int(hit_sy),
                flash_n,
                seed_base ^ 0x9E3779B9
            )

    def _lcg(self, seed: int) -> int:
        return lcg_next_u32(seed)

    def _pick_text(self, items: list[str], idx: int) -> str:
        n = len(items)
        if n <= 0:
            return ""
        return items[idx % n]

    def _code_shard_text(self, idx: int) -> str:
        return self._pick_text(self._PRIME_WORDS, idx)

    def _entity_whisper_text(self, idx: int) -> str:
        return self._pick_text(self._ENTITY_WORDS, idx)

    def _entity_error_text(self, idx: int) -> str:
        return self._pick_text(self._ENTITY_ERRORS, idx)

    def _prime_error_text(self, idx: int) -> str:
        return self._pick_text(self._PRIME_ERRORS, idx)

    def _queue_pursuer_error_text(self, variant_id: str) -> None:
        seed = self._pursuer_error_seed ^ int(self._pursuer_anim_t * 1000.0)
        seed = self._lcg(seed)
        self._pursuer_error_seed = seed
        if variant_id == "entity":
            self._pursuer_error_text = self._entity_error_text(seed)
            self._pursuer_error_color = Color.ORANGE
        else:
            self._pursuer_error_text = self._prime_error_text(seed)
            self._pursuer_error_color = Color.RED
        self._pursuer_error_t = 0.55

    def _draw_pursuer_error_overlay(self, screen_glitch_active: bool) -> None:
        if not screen_glitch_active:
            return
        if self._pursuer_error_t <= 0.0:
            return
        txt = self._pursuer_error_text
        if txt == "":
            return
        text_w = len(txt) * 6
        tx = 239 - 4 - text_w
        if tx < 0:
            tx = 0
        ty = 136 - 4 - 6
        color = self._pursuer_error_color
        print(txt, tx, ty, color, True, 1, False)

    def draw_glitch_pursuer_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning
    ) -> None:
        self._draw_pursuer_glitch_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            profile,
            False
        )

    def draw_prime_pursuer_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning
    ) -> None:
        # Prime Entity должен снова вести себя как "большой босс":
        # визуальный радиус не может быть меньше ширины дороги.
        self._draw_pursuer_glitch_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            profile,
            True
        )

    def _draw_pursuer_glitch_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning,
        clamp_to_road: bool
    ) -> None:
        r = int(profile.body_radius_chase)
        if pursuer_state == "NEAR":
            r = int(profile.body_radius_near)
        if clamp_to_road:
            min_by_road = int(road_half_px * 1.08)
            if min_by_road > r:
                r = min_by_road
        if r < 3:
            r = 3

        # Единое "ядро" без дублирования формы.
        core_color = Color.DARK_BLUE
        if pursuer_state == "NEAR":
            core_color = Color.BLUE
        circ(px, py, r, core_color)
        core_r = r - 4
        if core_r < 2:
            core_r = 2
        circ(px, py, core_r, Color.CYAN)
        circb(px, py, r + 1, Color.LIGHT_BLUE)
        # RGB split как контуры, а не как второй "клон" тела.
        circb(px - 1, py, r, Color.CYAN)
        circb(px + 1, py, r, Color.BLUE)

        # Рваные "сканлайны" поверх ядра.
        seed = seed_base
        lines_n = 7 + int(r * 0.55)
        if pursuer_state == "NEAR":
            lines_n += int(r * 0.35)
        i = 0
        while i < lines_n:
            seed = self._lcg(seed)
            if pursuer_state != "NEAR" and (seed & 3) == 0:
                i += 1
                continue
            y_off = int(seed % (r * 2 + 3)) - (r + 1)
            seed = self._lcg(seed)
            half = r - int(abs(y_off) * 0.4) + int(seed & 1)
            if half < 1:
                half = 1
            seed = self._lcg(seed)
            x_jit = int(r * 0.22)
            if x_jit < 2:
                x_jit = 2
            x_off = int(seed % (x_jit * 2 + 1)) - x_jit
            color = Color.CYAN
            if (seed & 1) == 0:
                color = Color.LIGHT_BLUE
            if (seed & 7) == 0:
                color = Color.WHITE
            line(
                px - half + x_off,
                py + y_off,
                px + half + x_off,
                py + y_off,
                color
            )
            i += 1

        # Кодовые осколки: единый стиль (как в NEAR), но с разной интенсивностью.
        # В CHASE рендерим мягче, в NEAR плотнее.
        if pursuer_state == "FAR":
            return
        is_near = pursuer_state == "NEAR"
        seed = self._lcg(seed)

        shards = int(profile.code_shard_count_chase)
        if is_near:
            shards = int(profile.code_shard_count_near)
        if shards < 1:
            shards = 1

        inner_r = float(profile.code_shard_radius_inner)
        outer_r = float(profile.code_shard_radius_outer)
        if inner_r < 0.0:
            inner_r = 0.0
        if outer_r < 1.0:
            outer_r = 1.0
        if outer_r < inner_r:
            t = inner_r
            inner_r = outer_r
            outer_r = t
        # Осколки должны быть СНАРУЖИ тела преследователя.
        min_outer_shell = float(r) + 8.0
        if inner_r < min_outer_shell:
            inner_r = min_outer_shell
        if outer_r < inner_r + 8.0:
            outer_r = inner_r + 8.0
        up_bias = float(profile.code_shard_up_bias)
        inner2 = inner_r * inner_r
        outer2 = outer_r * outer_r

        j = 0
        while j < shards:
            seed = self._lcg(seed)
            angle = (float(seed & 4095) / 4095.0) * math.pi * 2.0
            seed = self._lcg(seed)
            dist_n = float(seed & 1023) / 1023.0
            dist = (inner2 + (outer2 - inner2) * dist_n) ** 0.5
            anchor_x = px + int(math.cos(angle) * dist)
            anchor_y = py + int(math.sin(angle) * dist - up_bias)
            seed = self._lcg(seed)
            txt = self._code_shard_text(seed)
            color = Color.LIGHT_BLUE
            if is_near and (seed & 1) != 0:
                color = Color.CYAN
            elif (seed & 15) == 0:
                color = Color.WHITE
            text_w = len(txt) * 6
            sx = anchor_x - (text_w // 2)
            sy = anchor_y
            if sy >= -6 and sy <= 130:
                if sx >= -text_w and sx <= 239:
                    print(txt, sx, sy, color)
            j += 1

    def draw_entity_pursuer_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        profile: PursuerVariantTuning
    ) -> None:
        r = int(profile.body_radius_chase)
        if pursuer_state == "NEAR":
            r = int(profile.body_radius_near)
        if r < 3:
            r = 3

        core_color = Color.DARK_BLUE
        if pursuer_state == "NEAR":
            core_color = Color.BLUE
        circ(px, py, r, core_color)
        inner = r - 2
        if inner < 2:
            inner = 2
        circ(px, py, inner, Color.CYAN)
        ring_color = Color.CYAN
        if pursuer_state == "NEAR":
            ring_color = Color.WHITE
        circb(px, py, r + 1, ring_color)
        eye_half = 1
        if r >= 6:
            eye_half = 2
        line(px - eye_half, py, px + eye_half, py, Color.WHITE)

        seed = seed_base
        trail_n = 3
        if pursuer_state == "NEAR":
            trail_n = 5
        i = 0
        while i < trail_n:
            seed = self._lcg(seed)
            x_off = int(seed % 3) - 1
            y0 = py + r + 1 + i * 2
            y1 = y0 + 1
            c = Color.DARK_BLUE
            if (seed & 1) != 0:
                c = Color.BLUE
            line(px + x_off, y0, px + x_off, y1, c)
            i += 1

        labels_n = 2
        if pursuer_state == "NEAR":
            labels_n = 3
        orbit_r = float(r) + 13.0
        if pursuer_state == "NEAR":
            orbit_r += 3.0
        t = self._pursuer_anim_t
        j = 0
        while j < labels_n:
            seed = self._lcg(seed)
            txt = self._entity_whisper_text(seed)
            seed = self._lcg(seed)
            a = (float(seed & 4095) / 4095.0) * math.pi * 2.0
            a += t * 0.65 + float(j) * 1.2
            wobble = 1.2 * math.sin(t * 2.4 + float(seed & 255) * 0.03)
            dist = orbit_r + wobble
            ax = px + int(math.cos(a) * dist)
            ay = py + int(math.sin(a) * dist * 0.72 - 4.0)
            color = Color.LIGHT_BLUE
            if pursuer_state == "NEAR" and (seed & 1) != 0:
                color = Color.CYAN
            elif (seed & 31) == 0:
                color = Color.WHITE
            text_w = len(txt) * 5
            sx = ax - (text_w // 2)
            sy = ay
            if sy >= -6 and sy <= 130:
                if sx >= -text_w and sx <= 239:
                    print(txt, sx, sy, color, True, 1, True)
            j += 1

    def draw_entity_pursuer_strike(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        dx = float(tx - px)
        dy = float(ty - py)
        d2 = dx * dx + dy * dy
        if d2 <= 0.0001:
            return
        inv = 1.0 / (d2 ** 0.5)
        nx = -dy * inv
        ny = dx * inv
        segs = 4
        seed = seed_base
        prev_x = float(px)
        prev_y = float(py)
        i = 1
        while i <= segs:
            t = float(i) / float(segs)
            x = float(px) + dx * t
            y = float(py) + dy * t
            if i < segs:
                seed = self._lcg(seed)
                jitter = ((float(seed & 255) / 255.0) * 2.0 - 1.0)
                amp = 1.0 + 4.0 * flash_n
                x += nx * jitter * amp
                y += ny * jitter * amp
            line(int(prev_x), int(prev_y), int(x), int(y), Color.LIGHT_BLUE)
            if flash_n > 0.45:
                line(int(prev_x), int(prev_y) + 1, int(x), int(y) + 1, Color.WHITE)
            prev_x = x
            prev_y = y
            i += 1

    def draw_glitch_pursuer_strike(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        self._draw_pursuer_strike_lightning(px, py, tx, ty, flash_n, seed_base)

    def _draw_pursuer_strike_lightning(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        dx = float(tx - px)
        dy = float(ty - py)
        d2 = dx * dx + dy * dy
        if d2 <= 0.0001:
            return
        inv = 1.0 / (d2 ** 0.5)
        nx = -dy * inv
        ny = dx * inv

        seed = seed_base
        segs = 7
        prev_x = float(px)
        prev_y = float(py)
        i = 1
        while i <= segs:
            t = float(i) / float(segs)
            x = float(px) + dx * t
            y = float(py) + dy * t
            if i < segs:
                seed = self._lcg(seed)
                jitter = ((float(seed & 255) / 255.0) * 2.0 - 1.0)
                amp = 2.0 + 7.0 * flash_n
                x += nx * jitter * amp
                y += ny * jitter * amp
            line(int(prev_x), int(prev_y), int(x), int(y), Color.CYAN)
            line(int(prev_x) + 1, int(prev_y), int(x) + 1, int(y), Color.BLUE)
            if flash_n > 0.55:
                line(int(prev_x), int(prev_y) + 1, int(x), int(y) + 1, Color.WHITE)
            prev_x = x
            prev_y = y
            i += 1

    def _camera_forward(self, logic: DriveLogic) -> tuple[float, float]:
        heading_x = logic.fwd_x
        heading_y = logic.fwd_y

        if not self._cam_inited:
            self._cam_fwd_x = heading_x
            self._cam_fwd_y = heading_y
            self._cam_vel_x = heading_x
            self._cam_vel_y = heading_y
            self._cam_angle = math.atan2(self._cam_fwd_y, self._cam_fwd_x)
            self._cam_ang_vel = 0.0
            self._cam_inited = True
            return (self._cam_fwd_x, self._cam_fwd_y)

        vel_speed = (logic.vx * logic.vx + logic.vy * logic.vy) ** 0.5

        speed_blend = self._speed_blend(vel_speed)
        if logic.v_forward < 0.0:
            speed_blend = 0.0
        if speed_blend <= 0.0:
            self._cam_vel_x = heading_x
            self._cam_vel_y = heading_y
        else:
            raw_x, raw_y = self._normalize_or_fallback(
                logic.vx, logic.vy, self._cam_vel_x, self._cam_vel_y
            )
            vel_lerp = self._clamp(float(TUNING.DRIVE.cam_vel_dir_lerp), 0.0, 1.0)
            self._cam_vel_x += (raw_x - self._cam_vel_x) * vel_lerp
            self._cam_vel_y += (raw_y - self._cam_vel_y) * vel_lerp
            self._cam_vel_x, self._cam_vel_y = self._normalize_or_fallback(
                self._cam_vel_x, self._cam_vel_y, heading_x, heading_y
            )

        target_x = heading_x * (1.0 - speed_blend) + self._cam_vel_x * speed_blend
        target_y = heading_y * (1.0 - speed_blend) + self._cam_vel_y * speed_blend
        target_x, target_y = self._normalize_or_fallback(target_x, target_y, heading_x, heading_y)

        target_angle = math.atan2(target_y, target_x)
        dt = float(TUNING.CORE.dt)
        target_angle = self._cap_low_speed_target_angle(target_angle, speed_blend, dt)
        self._step_camera_spring(target_angle, dt)
        self._cam_fwd_x = math.cos(self._cam_angle)
        self._cam_fwd_y = math.sin(self._cam_angle)
        return (self._cam_fwd_x, self._cam_fwd_y)

    def _speed_blend(self, speed: float) -> float:
        min_speed = float(TUNING.DRIVE.cam_vel_min_speed)
        full_speed = float(TUNING.DRIVE.cam_vel_full_speed)
        return self._speed_blend_range(speed, min_speed, full_speed)

    def _speed_blend_range(self, speed: float, min_speed: float, full_speed: float) -> float:
        if speed <= min_speed:
            return 0.0
        denom = full_speed - min_speed
        if denom <= 0.0:
            return 1.0
        t = self._clamp((speed - min_speed) / denom, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    def _step_camera_spring(self, target_angle: float, dt: float) -> None:
        if dt <= 0.0:
            self._cam_angle = target_angle
            self._cam_ang_vel = 0.0
            return

        freq_hz = float(TUNING.DRIVE.cam_spring_freq_hz)
        damping = float(TUNING.DRIVE.cam_spring_damping)
        if freq_hz <= 0.0:
            self._cam_angle = target_angle
            self._cam_ang_vel = 0.0
            return
        if damping < 0.0:
            damping = 0.0

        omega = 2.0 * math.pi * freq_hz
        delta = self._wrap_angle(target_angle - self._cam_angle)
        accel = (omega * omega) * delta - (2.0 * damping * omega) * self._cam_ang_vel
        self._cam_ang_vel += accel * dt
        self._cam_angle = self._wrap_angle(self._cam_angle + self._cam_ang_vel * dt)

    def _cap_low_speed_target_angle(
        self,
        target_angle: float,
        speed_blend: float,
        dt: float
    ) -> float:
        if dt <= 0.0:
            return target_angle
        cap_blend_max = float(TUNING.DRIVE.cam_low_speed_cap_blend_max)
        if cap_blend_max <= 0.0:
            return target_angle
        if speed_blend >= cap_blend_max:
            return target_angle

        t = self._clamp(speed_blend / cap_blend_max, 0.0, 1.0)
        min_rate = float(TUNING.DRIVE.cam_low_speed_yaw_rate_min_deg)
        max_rate = float(TUNING.DRIVE.cam_low_speed_yaw_rate_max_deg)
        max_rate_deg = min_rate + (max_rate - min_rate) * t
        max_step = math.radians(max_rate_deg) * dt
        delta = self._wrap_angle(target_angle - self._cam_angle)
        if delta > max_step:
            return self._wrap_angle(self._cam_angle + max_step)
        if delta < -max_step:
            return self._wrap_angle(self._cam_angle - max_step)
        return target_angle

    def _draw_car_ttri(self, pose: CarPose2D) -> None:
        sx0 = self._CAR_SRC_X0
        sy0 = self._CAR_SRC_Y0
        sx1 = self._CAR_SRC_X1
        sy1 = self._CAR_SRC_Y1
        src_shift_x = self._CAR_SOURCE_REPACK_SHIFT_X
        rx0, ry0 = pose.sprite_px_to_screen(sx0 + src_shift_x, sy0)
        rx1, ry1 = pose.sprite_px_to_screen(sx1 + src_shift_x, sy0)
        rx2, ry2 = pose.sprite_px_to_screen(sx1 + src_shift_x, sy1)
        rx3, ry3 = pose.sprite_px_to_screen(sx0 + src_shift_x, sy1)

        base_u = float((self._CAR_SPRITE_BASE_ID % 16) * 8)
        base_v = float((self._CAR_SPRITE_BASE_ID // 16) * 8)
        u0 = base_u + sx0
        v0 = base_v + sy0
        u1 = base_u + sx1
        v1 = base_v + sy1

        ttri(
            rx0, ry0,
            rx1, ry1,
            rx2, ry2,
            u0, v0,
            u1, v0,
            u1, v1,
            0,
            self._CAR_CHROMAKEY
        )
        ttri(
            rx0, ry0,
            rx2, ry2,
            rx3, ry3,
            u0, v0,
            u1, v1,
            u0, v1,
            0,
            self._CAR_CHROMAKEY
        )

    @staticmethod
    def _normalize_or_fallback(
        x: float,
        y: float,
        fallback_x: float,
        fallback_y: float
    ) -> tuple[float, float]:
        l2 = x * x + y * y
        if l2 > 0.000001:
            inv = 1.0 / (l2 ** 0.5)
            return (x * inv, y * inv)
        return (fallback_x, fallback_y)

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        if value < min_value:
            return min_value
        if value > max_value:
            return max_value
        return value

    @staticmethod
    def _round_to_int(value: float) -> int:
        if value >= 0.0:
            return int(value + 0.5)
        return int(value - 0.5)

    @staticmethod
    def _wrap_angle(angle: float) -> float:
        pi = math.pi
        two_pi = 2.0 * pi
        while angle > pi:
            angle -= two_pi
        while angle < -pi:
            angle += two_pi
        return angle
