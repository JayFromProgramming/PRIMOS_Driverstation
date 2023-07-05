import multiprocessing
import time
import threading

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

import controller
from QT5_Classes.CommandsUI import CommandsUI
from ROS.ROSInterface import ROSInterface
# from ROS.RobotState import RobotState

import logging

logging = logging.getLogger(__name__)


class DriverStationUI:

    def __init__(self, robot: ROSInterface):

        self.robot = robot
        self.last_redraw = 0  # type: int

        self.robot_state = robot
        try:
            self.xbox_controller = controller.XboxController()
        except Exception as e:
            logging.error(f"Error initializing controller: {e}")
            self.xbox_controller = None

        self.window = QMainWindow()
        self.armed = False

        # self.window.showMaximized()

        self.commands_ui = CommandsUI(self.robot, parent=self.window)
        self.window.resize(self.commands_ui.width(), self.commands_ui.height())

        self.commands_ui.move(0, 0)

        # Attach the resize event
        self.window.resizeEvent = self.resizeEvent
        self.window.show()

        threading.Thread(target=self.controller_read_loop).start()
        # threading.Thread(target=self.connection_check_loop).start()
        # multiprocessing.Process(target=self.controller_read_loop).start()

    def connection_check_loop(self):
        """Loop to check the connection to the ROS bridge"""
        while True:
            if not self.robot.is_connected:
                logging.error("Lost connection to ROS bridge")
                # Update the name of the window to indicate the connection status
                self.window.setWindowTitle(f"PRIMROSE Driver Station - Disconnected")
            else:
                # Update the name of the window to indicate the connection status
                self.window.setWindowTitle(f"PRIMROSE DRiver Station - Connected")
            time.sleep(1)

    def controller_read_loop(self):
        """Loop for the joystick"""
        modules = ["Front_Left", "Front_Right", "Rear_Left", "Rear_Right"]
        # Read the controller while the window is open
        while True:
            try:
                # Apply deadbands to the joystick
                forward = self.xbox_controller.LeftJoystickY if abs(self.xbox_controller.LeftJoystickY) > 0.15 else 0
                turn = self.xbox_controller.RightJoystickX if abs(self.xbox_controller.RightJoystickX) > 0.15 else 0
                lift = self.xbox_controller.RightJoystickY if abs(self.xbox_controller.RightJoystickY) > 0.15 else 0

                try:
                    # self.robot.get_state("/driv/cmd_vel").value = \
                    #     {"linear": {"x": forward, "y": 0, "z": 0}, "angular": {"x": 0, "y": 0, "z": turn}}
                    for quarter_module in modules:
                        self.robot.get_state(f"/mciu/{quarter_module}/odrive/input").value = [4, int(forward * 1000)]
                        self.robot.get_state(f"/mciu/{quarter_module}/actuators/input").value = [2, int(lift * 50), 0]
                        self.robot.get_state(f"/mciu/{quarter_module}/actuators/input").value = [2, int(turn * 50), 1]
                except Exception as e:
                    logging.error(f"Error writing to ROS: {e}")

                if self.xbox_controller.B:  # Emergency stop all motors
                    try:
                        for quarter_modules in modules:
                            self.robot.get_state(f"/mciu/{quarter_modules}/odrive/input").value = [0]
                        self.robot.get_state("/mciu/Trencher/odrive/input").value = [0]
                        self.robot.get_state("/mciu/Conveyor/odrive/input").value = [0]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")
                elif self.xbox_controller.A:
                    try:
                        for quarter_modules in modules:
                            self.robot.get_state(f"/mciu/{quarter_modules}/odrive/input").value = [3, 2]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")

                # Trencher controls
                if self.xbox_controller.X:  # Is actually Y for some reason
                    try:  # Set the control mode for the trencher and conveyor
                        self.robot.get_state("/mciu/Rear_Left/odrive/input").value = [3, 2, 2]
                        self.robot.get_state("/mciu/Trencher/odrive/input").value = [3, 2, 2]
                        self.robot.get_state("/mciu/Conveyor/odrive/input").value = [3, 2, 2]
                        self.robot.get_state("/mciu/Conveyor/odrive/input").value = [4, 1000]
                        self.armed = True
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")

                if self.xbox_controller.RightTrigger > -0.1 and self.xbox_controller.LeftTrigger > 0.6:
                    self.robot.get_state("/mciu/Conveyor/odrive/input").value = [4, 5000]
                    try:
                        if self.xbox_controller.LeftBumper:  # Reverse Trencher
                            self.robot.get_state("/driv/Trencher/throttle").value = int(self.xbox_controller.RightTrigger * 100)
                        else:
                            self.robot.get_state("/driv/Trencher/throttle").value = int(self.xbox_controller.RightTrigger * -100)
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")
                else:
                    try:
                        self.robot.get_state("/driv/Trencher/throttle").value = 0
                        self.robot.get_state("/mciu/Conveyor/odrive/input").value = [4, 0]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")

                if self.xbox_controller.Y:  # Is actually X for some reason
                    try:
                        for quarter_modules in modules:
                            self.robot.get_state(f"/mciu/{quarter_modules}/odrive/input").value = [2]  # Clear errors

                        self.robot.get_state("/mciu/Conveyor/odrive/input").value = [2]
                        self.robot.get_state("/mciu/Trencher/odrive/input").value = [2]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")

                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Error reading controller: {e}")

                time.sleep(5)

    # On resize adjust the positions of the widgets
    def resizeEvent(self, event):
        pass
