from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import trace

    from ...contracts import Tuning
    from ...core.run_state import RunState
    from .drive_logic_core import DriveLogic


class DriveTelemetry:
    """Сборщик телеметрии DRIVE для тюнинга и отладки.

    Держим это отдельным классом, чтобы DriveScene не превращалась в комбайн
    из логики + рендера + логгинга.

    Примечание про PocketPy: избегаем keyword-аргументов в вызовах (иногда ведут себя
    нестабильно), поэтому API сделан позиционным.
    """

    def __init__(self, every_frames: int, max_lines: int) -> None:
        self._every = int(every_frames)
        self._max = int(max_lines)
        self._lines: list[str] = []
        self._t = 0.0
        self._frame = 0
        self._offroad = False

    def begin(self, seed: int, mode: str, tuning: Tuning) -> None:
        """Начинает новый лог для сегмента."""
        self._lines = []
        self._t = 0.0
        self._frame = 0
        self._offroad = False

        self._add("drive telem begin seed=" + str(seed) + " mode=" + mode)

        d = tuning.DRIVE
        self._add(
            "drive telem tuning max_speed="
            + str(d.max_speed)
            + " accel="
            + str(d.accel)
            + " brake="
            + str(d.brake)
            + " coast="
            + str(d.coast_decel)
        )
        self._add(
            "drive telem tuning steer_rate="
            + str(d.steer_rate)
            + " ss_min="
            + str(d.steer_scale_min)
            + " ss_max="
            + str(d.steer_scale_max)
            + " slip_mult="
            + str(d.side_slip_speed_mult)
        )
        self._add(
            "drive telem tuning hb_decel="
            + str(d.handbrake_decel)
            + " hb_steer_mult="
            + str(d.handbrake_steer_mult)
            + " hb_grip_mult="
            + str(d.handbrake_grip_mult)
        )
        self._add(
            "drive telem tuning dash_impulse="
            + str(d.dash_impulse)
            + " dash_cd="
            + str(d.dash_cooldown)
        )

    def after_update(
        self,
        dt: float,
        steer: int,
        throttle: bool,
        brake: bool,
        handbrake: bool,
        dash_pressed: bool,
        run: RunState,
        logic: DriveLogic
    ) -> None:
        """Сэмплирует телеметрию не каждый кадр и отмечает важные события."""
        self._t += dt
        self._frame += 1

        if logic.offroad != self._offroad:
            self._offroad = logic.offroad
            self._add(
                "t="
                + f"{self._t:.2f}"
                + " EVENT surf="
                + ("OFF" if logic.offroad else "ROAD")
                + " s="
                + str(int(logic.road_s))
                + " d="
                + f"{logic.road_d:.2f}"
            )

        if self._every <= 0:
            return
        if (self._frame % self._every) != 0:
            return

        self._add(
            "t="
            + f"{self._t:.2f}"
            + " s="
            + str(int(logic.road_s))
            + " d="
            + f"{logic.road_d:.2f}"
            + " v="
            + f"{logic.v_forward:.2f}"
            + " side="
            + f"{logic.v_side:.2f}"
            + " spd="
            + f"{logic.speed:.2f}"
            + " steer="
            + str(steer)
            + " thr="
            + ("1" if throttle else "0")
            + " brk="
            + ("1" if brake else "0")
            + " hb="
            + ("1" if handbrake else "0")
            + " dash="
            + ("1" if dash_pressed else "0")
            + " ss="
            + f"{logic.dbg_steer_scale:.2f}"
            + " grip="
            + f"{logic.dbg_effective_grip:.2f}"
            + " damp="
            + f"{logic.dbg_side_damp:.2f}"
            + " surf="
            + ("OFF" if logic.offroad else "ROAD")
            + " fuel="
            + f"{run.car_fuel:.2f}"
            + " hp="
            + f"{run.car_hp:.2f}"
        )

    def dump(self, reason: str) -> None:
        """Печатает накопленный лог в консоль через `trace`."""
        trace("drive telem dump reason=" + reason +
              " lines=" + str(len(self._lines)))
        i = 0
        while i < len(self._lines):
            trace(self._lines[i])
            i += 1
        trace("drive telem end")
        self._lines = []

    def _add(self, line: str) -> None:
        if self._max > 0 and len(self._lines) >= self._max:
            return
        self._lines.append(line)
