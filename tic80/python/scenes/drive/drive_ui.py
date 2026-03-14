from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb, line, print, rect, rectb

    from ...contracts import PursuerVariantTuning
    from ...core.controls.actions import Action
    from ...core.game_state import GameState
    from ...core.palette import Color
    from ...core.run_state import RunState
    from ...core.ui.prompts import ui_prompt_for_action, ui_prompt_gap_join
    from ...core.ui.rich_text import ui_rich_has_glyph_tokens, ui_rich_print, ui_rich_text_width
    from ...core.text_layout import text_center_x, text_max_chars, text_trim, text_width
    from ...data.tuning import TUNING
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.pursuer_chase import PURSUER_STATE_CHASE, PURSUER_STATE_FAR, PURSUER_STATE_NEAR, PursuerState


class DriveUi:
    def draw_stats(self, run: RunState, logic: DriveLogic) -> None:
        """Рисует UI-статы (не debug overlay): HP/FUEL/SPEED как шкалы + числа.

        Позиция снизу, чтобы не перекрывать дорогу и не конфликтовать с HUD-рулём/слипом.
        """
        x, y, w, h, gap = self.hud_bars_layout()

        hp_max = float(TUNING.PROFILE.start_garage_hp)
        if hp_max <= 0.0:
            hp_max = 1.0
        fuel_max = float(TUNING.PROFILE.start_garage_fuel)
        if fuel_max <= 0.0:
            fuel_max = 1.0
        spd_max = float(TUNING.DRIVE.feedback_speed_ref)
        if spd_max <= 0.0:
            spd_max = 1.0

        # SPEED
        spd = float(logic.speed)
        n = spd / spd_max
        if n < 0.0:
            n = 0.0
        if n > 1.0:
            n = 1.0
        rectb(x, y, w, h, Color.GREY)
        rect(x + 1, y + 1, int((w - 2) * n), h - 2, Color.BLUE)
        print("spd " + self.fmt2(spd), x + w + 4, y, Color.LIGHT_GREY)
        y += h + gap

        # FUEL
        fuel = float(run.car_fuel)
        n = fuel / fuel_max
        if n < 0.0:
            n = 0.0
        if n > 1.0:
            n = 1.0
        rectb(x, y, w, h, Color.GREY)
        rect(x + 1, y + 1, int((w - 2) * n), h - 2, Color.ORANGE)
        print("fuel " + self.fmt2(fuel), x + w + 4, y, Color.LIGHT_GREY)
        y += h + gap

        # HP
        hp = float(run.car_hp)
        n = hp / hp_max
        if n < 0.0:
            n = 0.0
        if n > 1.0:
            n = 1.0
        rectb(x, y, w, h, Color.GREY)
        rect(x + 1, y + 1, int((w - 2) * n), h - 2, Color.RED)
        print("hp  " + self.fmt2(hp), x + w + 4, y, Color.LIGHT_GREY)

    def hud_bars_layout(self) -> tuple[int, int, int, int, int]:
        """Возвращает расположение нижних баров (spd/fuel/hp) в HUD.

        Мы держим бары снизу:
        - они не закрывают дорогу,
        - они не мешают рулю/слипу,
        - игрок краем глаза всегда видит “ресурсы”.
        """
        x = 2
        # Чем уже шкала, тем меньше риск “залезть” цифрами на машину (которая по центру).
        w = 24
        h = 6
        gap = 2
        total_h = h * 3 + gap * 2

        # Экран TIC-80: 240x136.
        y = 120 - total_h - 2
        if y < 0:
            y = 0
        return x, y, w, h, gap

    def hud_wheel_layout(self) -> tuple[int, int, int]:
        """Возвращает позицию/размер руля в HUD.

        Вынесено в отдельный метод, чтобы индикаторы (руль/слип) были согласованы и
        не “разъезжались” при правках.
        """
        bars_x, bars_y, bars_w, bars_h, bars_gap = self.hud_bars_layout()
        r = 9

        # Руль чуть выше баров, а slip рисуем над рулём (в одну колонку).
        x = 12
        y = bars_y - (r + 6)
        if y < r + 2:
            y = r + 2
        return x, y, r

    def draw_steer_wheel(self, logic: DriveLogic) -> None:
        """Рисует простой индикатор руля в HUD (не debug overlay).

        Важно: мы показываем именно ввод руля (LEFT/RIGHT), а не фактическую траекторию.
        Это “язык управления”: игрок понимает, что он сейчас делает, даже если машина
        на высокой скорости/в заносе реагирует не так, как ожидается.

        Реализация без тригонометрии:
        - рисуем маленький круг-руль;
        - спица “раскрывается” по `dbg_steer_scale`:
          - на низкой скорости (scale≈1.0) спица сильнее влево/вправо (большой угол),
          - на высокой (scale≈0.0) почти вверх (руль “зажат”).
        - рядом показываем `steer x..`, чтобы было очевидно, почему на скорости рулится хуже.
        """
        x, y, r = self.hud_wheel_layout()
        color = Color.GREY
        circb(x, y, r, color)

        steer = logic.steer_input
        scale = logic.dbg_steer_scale
        if scale < 0.0:
            scale = 0.0
        if scale > 1.0:
            scale = 1.0

        d = TUNING.DRIVE
        denom = d.steer_scale_max - d.steer_scale_min
        n = 0.0
        if denom > 0.0001:
            n = (scale - d.steer_scale_min) / denom
        if n < 0.0:
            n = 0.0
        if n > 1.0:
            n = 1.0

        # Даже на высокой скорости руль не должен выглядеть “мертвым”.
        # Поэтому нормализованный множитель (0..1) переводим в визуальный диапазон:
        # - при scale=min будет небольшой, но заметный поворот
        # - при scale=max будет максимальный
        n_vis = 0.35 + 0.65 * n

        spoke = r - 1
        if steer < 0:
            sx = x - int(spoke * n_vis)
            sy = y - spoke
            line(x, y, sx, sy, color)
        elif steer > 0:
            sx = x + int(spoke * n_vis)
            sy = y - spoke
            line(x, y, sx, sy, color)
        else:
            line(x, y, x, y - spoke, color)

        print("steer x" + self.fmt2(scale), x + 12, y - 4, Color.LIGHT_GREY)

    def draw_slip_bar(self, logic: DriveLogic) -> None:
        """Рисует двусторонний индикатор заноса (slip) рядом с рулём в HUD.

        Мы хотим показать две вещи одновременно:
        - насколько сильно несёт (модуль)
        - куда несёт (знак)

        Определение slip (0..1):
        `slip = abs(v_side) / (abs(v_forward) + eps)`.

        Важно: это не “истина в последней инстанции”, а удобная метрика для игрока.
        Если v_forward почти ноль, делаем eps, чтобы не было скачков/деления на 0.
        """
        wheel_x, wheel_y, wheel_r = self.hud_wheel_layout()
        w = 46
        half = int(w / 2)
        x0 = wheel_x - half
        if x0 < 2:
            x0 = 2
        y0 = wheel_y - wheel_r - 8
        half = int(w / 2)
        cx = x0 + half

        v_fwd = logic.v_forward
        v_side = logic.v_side

        denom = abs(v_fwd) + TUNING.DRIVE.slip_eps_speed
        slip = abs(v_side) / denom
        if slip > 1.0:
            slip = 1.0

        # Основа шкалы.
        line(x0, y0, x0 + w, y0, Color.GREY)
        line(cx, y0 - 2, cx, y0 + 2, Color.GREY)

        # Заполнение: влево/вправо по знаку заноса.
        fill = int(half * slip)
        if fill < 0:
            fill = 0
        if v_side < 0.0:
            line(cx, y0, cx - fill, y0, Color.BLUE)
        elif v_side > 0.0:
            line(cx, y0, cx + fill, y0, Color.RED)

        print("slip", x0, y0 - 8, Color.LIGHT_GREY)

    def draw_controls_panel(self, state: GameState, logic: DriveLogic) -> None:
        x = self.hud_controls_right_x()
        rows = self._control_rows(state, logic)
        i = 0
        while i < len(rows):
            prompt, label, pressed, enabled = rows[i]
            self._draw_control_row(x, self.hud_controls_row_y(i), prompt, label, pressed, enabled)
            i += 1

    def hud_controls_right_x(self) -> int:
        return 238

    def hud_controls_row_y(self, row_index: int) -> int:
        _, bars_y, _, _, _ = self.hud_bars_layout()
        start_y = bars_y - 16
        if start_y < 18:
            start_y = 18
        return start_y + row_index * 8

    def _control_rows(self, state: GameState, logic: DriveLogic) -> list[tuple[str, str, bool, bool]]:
        steer_prompt = (
            ui_prompt_for_action(state, Action.NAV_LEFT)
            + "{sep}"
            + ui_prompt_for_action(state, Action.NAV_RIGHT)
        )
        steer_pressed = (
            state.controls.down(Action.NAV_LEFT)
            or state.controls.down(Action.NAV_RIGHT)
        )
        throttle_pressed = state.controls.down(Action.THROTTLE)
        brake_pressed = state.controls.down(Action.BRAKE)
        handbrake_pressed = state.controls.down(Action.HANDBRAKE)
        module_enabled = float(TUNING.DRIVE.dash_impulse) > 0.0 and not logic.finished()
        module_pressed = False
        if module_enabled:
            module_pressed = state.controls.down(Action.MODULE)
        return [
            (steer_prompt, "steer", steer_pressed, True),
            (ui_prompt_for_action(state, Action.THROTTLE), "throttle", throttle_pressed, True),
            (ui_prompt_for_action(state, Action.BRAKE), "brake", brake_pressed, True),
            (ui_prompt_for_action(state, Action.HANDBRAKE), "handbrake", handbrake_pressed, True),
            (ui_prompt_for_action(state, Action.MODULE), "module", module_pressed, module_enabled)
        ]

    def _draw_control_row(
        self,
        right_x: int,
        row_y: int,
        prompt: str,
        label: str,
        pressed: bool,
        enabled: bool
    ) -> None:
        gap = 3
        prompt_w = ui_rich_text_width(prompt)
        label_w = text_width(label, 6)
        prompt_x = right_x - prompt_w
        label_x = prompt_x - gap - label_w
        prompt_color = Color.GREY
        label_color = Color.LIGHT_GREY
        if pressed:
            prompt_color = Color.WHITE
            label_color = Color.WHITE
        elif not enabled:
            prompt_color = Color.DARK_GREY
            label_color = Color.DARK_GREY
        prompt_has_glyphs = ui_rich_has_glyph_tokens(prompt)
        ui_rich_print(prompt, prompt_x, row_y, prompt_color, not prompt_has_glyphs)
        print(label, label_x, row_y, label_color)
        if not enabled:
            line(label_x, row_y + 3, right_x, row_y + 3, Color.GREY)

    def draw_pursuer_hud(
        self,
        run_scrap: int,
        start_run_scrap: int,
        pursuer_dist_s: float,
        pursuer_state: PursuerState,
        profile: PursuerVariantTuning,
        pursuer_name: str,
        pursuer_name_color: int
    ) -> None:
        show = float(profile.show_dist_s)
        near = float(profile.near_dist_s)
        strike = float(profile.strike_begin_dist_s)

        d = float(pursuer_dist_s) - strike
        if d < 0.0:
            d = 0.0
        show_eff = show - strike
        near_eff = near - strike
        if show_eff < 0.0:
            show_eff = 0.0
        if near_eff < 0.0:
            near_eff = 0.0

        fill_n = 0.0
        if show_eff > near_eff:
            if d < near_eff:
                fill_n = 1.0
            elif d < show_eff:
                fill_n = (show_eff - d) / (show_eff - near_eff)
        if fill_n < 0.0:
            fill_n = 0.0
        if fill_n > 1.0:
            fill_n = 1.0

        # DIST: большой верхний бар по центру.
        dist_w = 120
        dist_h = 7
        dist_x = int((240 - dist_w) * 0.5)
        dist_y = 4
        rectb(dist_x, dist_y, dist_w, dist_h, Color.WHITE)
        fill_w = int((dist_w - 2) * fill_n)
        color = Color.BLUE
        if pursuer_state == PURSUER_STATE_FAR:
            color = Color.GREEN
        elif d > 100.0:
            color = Color.BLUE
        elif pursuer_state == PURSUER_STATE_CHASE:
            color = Color.ORANGE
        elif pursuer_state == PURSUER_STATE_NEAR:
            color = Color.RED
        if fill_w > 0:
            rect(dist_x + 1, dist_y + 1, fill_w, dist_h - 2, color)
        char_w = 6
        shown_dist_m = int(d + 0.5)
        if shown_dist_m < 0:
            shown_dist_m = 0
        title_prefix = "ANOMALY//"
        name_text = str(pursuer_name).strip()
        title_suffix = "//" + str(shown_dist_m) + "m"
        max_chars = text_max_chars(240, char_w, 2)
        name_max = max_chars - len(title_prefix) - len(title_suffix)
        if name_max < 1:
            name_max = 1
        name_text = text_trim(name_text, name_max, True)
        title_text = title_prefix + name_text + title_suffix
        title_x = text_center_x(title_text, 240, char_w, 2)
        title_y = dist_y + dist_h + 2
        print(title_prefix, title_x, title_y, Color.WHITE, True)
        name_x = title_x + text_width(title_prefix, char_w)
        print(name_text, name_x, title_y, pursuer_name_color, True)
        suffix_x = name_x + text_width(name_text, char_w)
        print(title_suffix, suffix_x, title_y, Color.WHITE, True)

        # SCRAP: слева под HP.
        bars_x, bars_y, bars_w, bars_h, bars_gap = self.hud_bars_layout()
        hp_y = bars_y + (bars_h + bars_gap) * 2
        scrap_y = hp_y + bars_h + bars_gap
        rectb(bars_x, scrap_y, bars_w, bars_h, Color.WHITE)
        scrap_now = max(0, int(run_scrap))
        scrap_start = int(start_run_scrap)
        scrap_n = 0.0
        if scrap_start > 0:
            scrap_n = float(scrap_now) / float(scrap_start)
        if scrap_n < 0.0:
            scrap_n = 0.0
        if scrap_n > 1.0:
            scrap_n = 1.0
        scrap_fill_w = int((bars_w - 2) * scrap_n)
        if scrap_fill_w > 0:
            rect(bars_x + 1, scrap_y + 1, scrap_fill_w,
                 bars_h - 2, Color.LIGHT_GREEN)
        print("scrap " + str(scrap_now), bars_x +
              bars_w + 4, scrap_y, Color.WHITE)

    def fmt2(self, value: float) -> str:
        """Форматирует число с ровно 2 знаками после запятой (без `.format`/`%`).

        PocketPy не дружит с частью CPython форматтеров. Чтобы UI не “прыгал” и всегда
        был `xx.yy`, используем простую ручную раскладку.
        """
        v = float(value)
        sign = ""
        if v < 0.0:
            sign = "-"
            v = -v
        scaled = int(v * 100.0 + 0.5)
        whole = scaled // 100
        frac = scaled - whole * 100
        if frac < 10:
            return sign + str(whole) + ".0" + str(frac)
        return sign + str(whole) + "." + str(frac)
