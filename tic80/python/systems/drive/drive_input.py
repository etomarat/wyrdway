from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp

    from ...core.input_buttons import Button


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


def read_drive_input(allow_dash: bool) -> DriveInput:
    steer = 0
    if btn(Button.LEFT):
        steer -= 1
    if btn(Button.RIGHT):
        steer += 1

    throttle = btn(Button.UP)
    brake = btn(Button.DOWN)
    handbrake = btn(Button.B)

    a_pressed = btnp(Button.A)
    dash_pressed = False
    if allow_dash and a_pressed:
        dash_pressed = True

    return DriveInput(steer, throttle, brake, handbrake, a_pressed, dash_pressed)
