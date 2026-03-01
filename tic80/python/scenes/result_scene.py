from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls

    from ..contracts import ResultEnterParams, SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color, ColorId
    from ..core.scene_ids import SceneId
    from ..core.ui.overlay_footer import ui_overlay_footer_draw
    from ..core.ui.overlay_layout import OverlayLayout
    from ..core.ui.overlay_modal import (
        ui_overlay_modal_centered_box,
        ui_overlay_modal_draw_centered_lines,
        ui_overlay_modal_draw_chrome
    )
    from ..core.ui.prompts import ui_prompt_for_action
    from ..core.ui.prompts import ui_prompt_with_text
else:
    OverlayLayout = dict


class ResultScene:
    SCENE_ID = SceneId.RESULT
    OVERLAY_W = 216
    OVERLAY_H = 104
    OVERLAY_HEADER_TEXT_OFFSET_Y = 9
    OVERLAY_BODY_TOP_OFFSET_Y = 24
    OVERLAY_FOOTER_LINE_OFFSET_Y = 84
    OVERLAY_FOOTER_TEXT_OFFSET_Y = 88

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._title = "MISSION REPORT"
        self._title_color: ColorId = Color.WHITE
        self._subtitle = ""
        self._subtitle_color: ColorId = Color.LIGHT_GREY
        self._lines: list[tuple[str, ColorId]] = []
        self._cta = "CONTINUE TO GARAGE"
        self._cta_color: ColorId = Color.WHITE

    def _set_layout(
        self,
        title: str,
        title_color: ColorId,
        subtitle: str,
        subtitle_color: ColorId,
        lines: list[tuple[str, ColorId]],
        cta: str,
        cta_color: ColorId
    ) -> None:
        self._title = title
        self._title_color = title_color
        self._subtitle = subtitle
        self._subtitle_color = subtitle_color
        self._lines = lines
        self._cta = cta
        self._cta_color = cta_color

    def _reason_line(self, reason: str) -> str:
        if reason == "OUT OF FUEL":
            return "Your fuel reserves reached zero"
        if reason == "CAR DESTROYED":
            return "Your car could not survive the route"
        if reason == "POI TIMEOUT":
            return "You stayed at the site too long"
        if reason == "CHASE INTERRUPTED":
            return "Chase state collapsed before extraction"
        if reason == "RUN INTERRUPTED":
            return "Run session interrupted before return"
        return str(reason)

    def _build_rollback_layout(self, reason: str, theseus_gain: int) -> None:
        lines: list[tuple[str, ColorId]] = [
            ("Run lost. Reverted to last save", Color.WHITE),
            (self._reason_line(reason), Color.ORANGE),
            ("Theseus corruption: +" + str(theseus_gain), Color.RED),
            ("Refit in garage and run again", Color.YELLOW)
        ]
        self._set_layout(
            "RUN FAILED",
            Color.RED,
            "Reality anchor restored",
            Color.LIGHT_GREY,
            lines,
            "CONTINUE TO GARAGE",
            Color.RED
        )

    def _build_no_run_layout(self, fallback: str | None) -> None:
        lines: list[tuple[str, ColorId]] = [("No run data available", Color.LIGHT_GREY)]
        title = "RESULT"
        subtitle = "Return to garage"
        if fallback is not None:
            title = str(fallback)
        self._set_layout(
            title,
            Color.WHITE,
            subtitle,
            Color.LIGHT_GREY,
            lines,
            "CONTINUE TO GARAGE",
            Color.WHITE
        )

    def _build_run_report_layout(
        self,
        poi_action: str,
        delivered_scrap: int,
        fuel_recovered: int
    ) -> None:
        title = "RETURN COMPLETE"
        title_color: ColorId = Color.CYAN
        subtitle = "You reached base safely"
        subtitle_color: ColorId = Color.LIGHT_BLUE
        detail_line = "No loot collected"
        detail_color: ColorId = Color.LIGHT_GREY
        cta_color: ColorId = Color.WHITE
        if poi_action == "loot":
            title = "EXTRACTION COMPLETE"
            title_color = Color.LIGHT_GREEN
            subtitle = "Loot secured and delivered"
            subtitle_color = Color.WHITE
            detail_line = "High-risk raid paid off"
            detail_color = Color.GREEN
            cta_color = Color.LIGHT_GREEN
        elif poi_action == "leave":
            title = "RETREAT COMPLETE"
            title_color = Color.YELLOW
            subtitle = "You pulled out before looting"
            subtitle_color = Color.LIGHT_GREY
            detail_line = "No site loot collected"
            detail_color = Color.YELLOW
            cta_color = Color.YELLOW
        elif poi_action == "timeout":
            title = "SITE TIMEOUT"
            title_color = Color.ORANGE
            subtitle = "Extraction was not secured"
            subtitle_color = Color.LIGHT_GREY
            detail_line = "No loot secured from the site"
            detail_color = Color.ORANGE
            cta_color = Color.ORANGE
        lines: list[tuple[str, ColorId]] = [
            (detail_line, detail_color),
            ("Scrap delivered: +" + str(delivered_scrap), Color.LIGHT_GREEN),
            ("Fuel recovered: +" + str(fuel_recovered), Color.YELLOW)
            # ("Continue in garage", Color.LIGHT_GREY)
        ]
        self._set_layout(
            title,
            title_color,
            subtitle,
            subtitle_color,
            lines,
            "CONTINUE TO GARAGE",
            cta_color
        )

    def enter(self, params: SceneEnterParams = None) -> None:
        fallback = None
        if params is not None:
            if not isinstance(params, ResultEnterParams):
                raise TypeError("ResultScene.enter expects ResultEnterParams")
            fallback = params.text

        run = self._state.run
        if run is None:
            reason, theseus_gain = self._state.consume_rollback_notice()
            if reason is not None:
                self._build_rollback_layout(reason, theseus_gain)
                return
            self._build_no_run_layout(fallback)
            return

        delivered_scrap = 0
        for item in run.inventory_items():
            if item.id == "scrap":
                delivered_scrap += item.qty

        fuel_recovered = 0
        poi_action = "unknown"
        if run.delta is not None:
            delta = run.delta
            fuel_recovered = delta.fuel_gained
            if delta.poi_action is not None:
                poi_action = str(delta.poi_action)

        self._build_run_report_layout(poi_action, delivered_scrap, fuel_recovered)

    def update(self, dt: float) -> None:
        if self._state.controls.pressed(Action.CONFIRM):
            self._state.apply_run_results()
            self._nav.go(SceneId.GARAGE)

    def _overlay_layout(self) -> OverlayLayout:
        box_x, box_y = ui_overlay_modal_centered_box(self.OVERLAY_W, self.OVERLAY_H)
        return {
            "box_x": box_x,
            "box_y": box_y,
            "box_w": self.OVERLAY_W,
            "box_h": self.OVERLAY_H,
            "header_text_y": box_y + self.OVERLAY_HEADER_TEXT_OFFSET_Y,
            "body_top": box_y + self.OVERLAY_BODY_TOP_OFFSET_Y,
            "footer_line_y": box_y + self.OVERLAY_FOOTER_LINE_OFFSET_Y,
            "footer_text_y": box_y + self.OVERLAY_FOOTER_TEXT_OFFSET_Y,
            "slot_count": 1,
            "slot_weights": (1,),
            "slot_nav": 0,
            "slot_confirm": 0,
            "slot_cancel": 0
        }

    def _body_lines(self) -> list[tuple[str, ColorId]]:
        body: list[tuple[str, ColorId]] = []
        if self._subtitle != "":
            body.append((self._subtitle, self._subtitle_color))
            body.append(("", Color.WHITE))
        i = 0
        while i < len(self._lines):
            body.append(self._lines[i])
            i += 1
        return body

    def draw(self) -> None:
        cls(Color.BLACK)
        layout = self._overlay_layout()
        box_x, _box_y, box_w, _box_h, body_top, footer_line_y, footer_text_y = ui_overlay_modal_draw_chrome(
            layout,
            self._title,
            self._title_color,
            Color.BLACK,
            Color.DARK_GREY,
            Color.BLACK,
            Color.GREY
        )
        ui_overlay_modal_draw_centered_lines(
            self._body_lines(),
            box_x,
            box_w,
            body_top,
            8
        )
        prompt = ui_prompt_for_action(self._state, Action.CONFIRM)
        cta = ui_prompt_with_text(prompt, self._cta)
        ui_overlay_footer_draw(
            layout,
            [cta],
            [self._state.controls.down(Action.CONFIRM)],
            [False],
            footer_line_y,
            footer_text_y,
            Color.BLACK,
            Color.GREY,
            False,
            -1,
            self._cta_color
        )

    def exit(self) -> None:
        pass


def make_result_scene(nav: SceneNavigator) -> ResultScene:
    return ResultScene(nav)
