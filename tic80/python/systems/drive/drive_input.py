from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.controls.actions import Action
    from ...core.controls.input import Controls


class DriveInput:
    def __init__(
        self,
        steer: int,
        throttle: bool,
        brake: bool,
        handbrake: bool,
        dash_pressed: bool
    ) -> None:
        self.steer = steer
        self.throttle = throttle
        self.brake = brake
        self.handbrake = handbrake
        self.dash_pressed = dash_pressed


def read_drive_input(controls: Controls) -> DriveInput:
    steer = 0
    if controls.down(Action.NAV_LEFT):
        steer -= 1
    if controls.down(Action.NAV_RIGHT):
        steer += 1

    throttle = controls.down(Action.THROTTLE)
    brake = controls.down(Action.BRAKE)
    handbrake = controls.down(Action.HANDBRAKE)

    dash_pressed = controls.pressed(Action.MODULE)

    return DriveInput(steer, throttle, brake, handbrake, dash_pressed)
