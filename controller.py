import inputs
from inputs import get_gamepad
import math
import time
import threading

from loguru import logger as logging

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.connected = False
        self.last_update = time.time()
        self.usb_name = "Unknown"
        self._mapping = "Unknown"  # Set externally and used externally
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):  # return the buttons/triggers that you care about in this methode
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        a = self.A
        b = self.X  # b=1, x=2
        rb = self.RightBumper
        return [x, y, a, b, rb]

    def set_mapping(self, mapping):
        self._mapping = mapping

    @property
    def mapping(self):
        return self._mapping

    def on_disconnect(self):
        self.connected = False
        # Set all inputs to 0
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

    def _monitor_controller(self):
        while True:
            try:
                events = get_gamepad()
                self.connected = True
            except inputs.UnpluggedError:
                if self.connected:
                    logging.warning("Controller disconnected")
                events = []
                self.on_disconnect()
                time.sleep(5)
            for event in events:
                self.last_update = time.time()
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = -event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = -event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = -event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.X = event.state
                elif event.code == 'BTN_WEST':
                    self.Y = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state
                elif event.code == 'ABS_HAT0Y':
                    if event.state == -1:
                        self.UpDPad = 1
                        self.DownDPad = 0
                    elif event.state == 1:
                        self.DownDPad = 1
                        self.UpDPad = 0
                    else:
                        self.DownDPad = 0
                        self.UpDPad = 0
                elif event.code == 'ABS_HAT0X':
                    if event.state == -1:
                        self.LeftDPad = 1
                        self.RightDPad = 0
                    elif event.state == 1:
                        self.RightDPad = 1
                        self.LeftDPad = 0
                    else:
                        self.RightDPad = 0
                        self.LeftDPad = 0
                elif event.code == 'SYN_REPORT':
                    self.usb_name = event.device
                else:
                    logging.warning(f"Joystick returned unknown event: {event.code} - {event.state}")
            time.sleep(1/60)
