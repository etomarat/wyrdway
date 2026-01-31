from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import SceneNavigator
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId


class GarageScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self._state = nav.state
        self.note = "Press A to start run"

    def enter(self, params: object | None = None) -> None:
        pass

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            self._state.start_run()
            self._nav.go(SceneId.REGION_MAP)

    def draw(self) -> None:
        cls(0)
        print("GARAGE", 98, 40, 12)
        print("money=" + str(self._state.profile.money), 82, 60, 12)
        print("hp=" + str(self._state.profile.garage_hp), 94, 70, 12)
        print("fuel=" + str(round(self._state.profile.garage_fuel, 1)),
              82, 80, 12)
        print(self.note, 56, 100, 12)

    def exit(self) -> None:
        pass


def make_garage_scene(nav: "SceneNavigator") -> "GarageScene":
    return GarageScene(nav)
