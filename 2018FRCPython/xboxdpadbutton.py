
from enum import Enum
from wpilib.buttons import Button

class DPAD_BUTTON(Enum):
    DPAD_UP = 0
    DPAD_RIGHT = 1
    DPAD_DOWN = 2
    DPAD_LEFT = 3

class XboxDPadButton(Button):

    def __init__(self, controller, dtype):
        super().__init__()
        self.xbox_controller = controller
        self.dpad_type = dtype

    def get(self):
        retval = False

        if self.dpad_type == DPAD_BUTTON.DPAD_UP:
            if self.xbox_controller.getPOV() == 0:
                retval = True
        elif self.dpad_type == DPAD_BUTTON.DPAD_RIGHT:
            if self.xbox_controller.getPOV() == 90:
                retval = True
        elif self.dpad_type == DPAD_BUTTON.DPAD_DOWN:
            if self.xbox_controller.getPOV() == 180:
                retval = True
        elif self.dpad_type == DPAD_BUTTON.DPAD_LEFT:
            if self.xbox_controller.getPOV() == 270:
                retval = True

        return retval
