from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import SceneNavigator
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
        self._can_restart = False

    def enter(self, params: object | None = None) -> None:
        pass

    def update(self, dt: float) -> None:
        profile = self._profile
        self._can_restart = profile.garage_hp <= 0 or profile.garage_fuel <= 0

        if btnp(Button.A):
            self._state.save_profile()
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
            if self._can_restart:
                self._profile.reset()
                self._state.save_profile()

    def draw(self) -> None:
        cls(Color.BLACK)
        print("GARAGE", 98, 40, Color.WHITE)
        print("scrap=" + str(self._state.profile.scrap), 82, 60, Color.WHITE)
        print("hp=" + str(round(self._state.profile.garage_hp, 1)),
              82, 70, Color.WHITE)
        print("fuel=" + str(round(self._state.profile.garage_fuel, 1)),
              82, 80, Color.WHITE)
        print("Z = START", 86, 100, Color.WHITE)
        print("X = REPAIR (-" + str(TUNING.PROFILE.repair_cost) + ")",
              86, 110, Color.WHITE)
        if self._can_restart:
            print("A = NEW GAME (RESET)", 86, 120, Color.WHITE)

    def exit(self) -> None:
        pass


def make_garage_scene(nav: SceneNavigator) -> "GarageScene":
    return GarageScene(nav)
