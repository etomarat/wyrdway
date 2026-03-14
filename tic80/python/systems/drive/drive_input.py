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
        a_pressed: bool,
        dash_pressed: bool
    ) -> None:
        self.steer = steer
        self.throttle = throttle
        self.brake = brake
        self.handbrake = handbrake
        self.a_pressed = a_pressed
        self.dash_pressed = dash_pressed


def read_drive_input(controls: Controls, allow_dash: bool) -> DriveInput:
    steer = 0
    if controls.down(Action.NAV_LEFT):
        steer -= 1
    if controls.down(Action.NAV_RIGHT):
        steer += 1

    throttle = controls.down(Action.THROTTLE)
    brake = controls.down(Action.BRAKE)
    handbrake = controls.down(Action.HANDBRAKE)

    a_pressed = controls.pressed(Action.CONFIRM)
    dash_pressed = False
    if allow_dash and controls.pressed(Action.MODULE):
        dash_pressed = True

    return DriveInput(steer, throttle, brake, handbrake, a_pressed, dash_pressed)
