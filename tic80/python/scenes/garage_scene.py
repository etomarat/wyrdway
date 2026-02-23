from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


class GarageScene:
    SCENE_ID = SceneId.GARAGE

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._profile = nav.state.profile
        self._confirm_new_game = False

    def enter(self, params: SceneEnterParams = None) -> None:
        self._confirm_new_game = False

    def update(self, dt: float) -> None:
        if self._confirm_new_game:
            if btnp(Button.A):
                self._state.start_new_game()
                self._confirm_new_game = False
            elif btnp(Button.B) or btnp(Button.X):
                self._confirm_new_game = False
            return

        if btnp(Button.A):
            self._state.start_run()
            self._nav.go(SceneId.REGION_MAP)
        elif btnp(Button.B):
            repaired = self._profile.repair(
                TUNING.PROFILE.repair_cost,
                TUNING.PROFILE.repair_hp,
                TUNING.PROFILE.start_garage_hp
            )
            if repaired:
                self._state.save_profile()
        elif btnp(Button.X):
            self._confirm_new_game = True

    def draw(self) -> None:
        cls(Color.BLACK)
        print("GARAGE", 98, 40, Color.WHITE)
        print("scrap=" + str(self._state.profile.scrap), 82, 60, Color.WHITE)
        print("hp=" + f"{self._state.profile.garage_hp:.2f}",
              82, 70, Color.WHITE)
        print("fuel=" + f"{self._state.profile.garage_fuel:.2f}",
              82, 80, Color.WHITE)
        if self._confirm_new_game:
            print("NEW GAME?", 84, 96, Color.WHITE)
            print("Z = CONFIRM RESET", 64, 106, Color.WHITE)
            print("X = CANCEL", 76, 116, Color.LIGHT_GREY)
            return
        print("Z = START", 86, 100, Color.WHITE)
        print("X = REPAIR (-" + str(TUNING.PROFILE.repair_cost) + ")",
              86, 110, Color.WHITE)
        print("X = NEW GAME", 86, 120, Color.WHITE)

    def exit(self) -> None:
        pass


def make_garage_scene(nav: SceneNavigator) -> GarageScene:
    return GarageScene(nav)
