from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import SceneNavigator
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


class GarageScene:
    SCENE_ID = SceneId.GARAGE

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._profile = nav.state.profile

    def enter(self, params: object | None = None) -> None:
        pass

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            self._state.start_run()
            self._nav.go(SceneId.REGION_MAP)
        elif btnp(Button.B):
            self._profile.repair(
                TUNING.PROFILE.repair_cost,
                TUNING.PROFILE.repair_hp,
                TUNING.PROFILE.start_garage_hp,
            )

    def draw(self) -> None:
        cls(0)
        print("GARAGE", 98, 40, 12)
        print("scrap=" + str(self._state.profile.scrap), 82, 60, 12)
        print("hp=" + str(self._state.profile.garage_hp), 94, 70, 12)
        print("fuel=" + str(round(self._state.profile.garage_fuel, 1)),
              82, 80, 12)
        print("A = START", 86, 100, 12)
        print("B = REPAIR (-" + str(TUNING.PROFILE.repair_cost) + ")",
              46, 110, 12)

    def exit(self) -> None:
        pass


def make_garage_scene(nav: SceneNavigator) -> "GarageScene":
    return GarageScene(nav)
