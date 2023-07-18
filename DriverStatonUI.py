import argparse
import multiprocessing
import time
import threading

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

import controller
from QT5_Classes.CommandsUI import CommandsUI
from ROS.ROSInterface import ROSInterface
# from ROS.RobotState import RobotState

from loguru import logger as logging

from Resources import Enumerators


class DriverStationUI:

    def __init__(self, robot: ROSInterface, args: argparse.Namespace):

        self.robot = robot
        self.last_redraw = 0  # type: int

        self.robot_state = robot
        logging.info("Initializing Driver Station UI")
        self.xbox_controller = controller.XboxController()

        self.window = QMainWindow()
        self.armed = False

        # self.window.showMaximized()

        self.commands_ui = CommandsUI(self.robot, parent=self.window, xbox_controller=self.xbox_controller)
        self.window.resize(self.commands_ui.width(), self.commands_ui.height())

        self.commands_ui.move(0, 0)

        # Attach the resize event
        # self.window.resizeEvent = self.resizeEvent
        # Disable resizing and maximize button
        self.window.setFixedSize(self.window.width(), self.window.height())
        self.window.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)

        if args.always_on_top:
            self.window.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)

        self.window.show()

        threading.Thread(target=self.controller_read_loop, daemon=True).start()

        # Start the timer for the connection check loop
        self.connection_check_timer = QtCore.QTimer()
        self.connection_check_timer.timeout.connect(self.connection_check_loop)
        self.connection_check_timer.start(1000)

    def connection_check_loop(self):
        """Loop to check the connection to the ROS bridge"""
        if not self.robot.is_connected:
            # logging.error("Lost connection to ROS bridge")
            # Update the name of the window to indicate the connection status
            self.window.setWindowTitle(f"PRIMROSE Driver Station - Disconnected")
        elif self.robot.is_connected and not self.xbox_controller.connected:
            # Update the name of the window to indicate the connection status
            self.window.setWindowTitle(f"PRIMROSE Driver Station - No Controller")
        else:
            # Update the name of the window to indicate the connection status
            self.window.setWindowTitle(f"PRIMROSE Driver Station - Connected")

    def controller_read_loop(self):
        """Loop for the joystick"""
        modules = ["Front_Left", "Front_Right", "Rear_Left", "Rear_Right"]
        # Read the controller while the window is open
        while True:
            time.sleep(0.1)
            try:
                if not self.robot.is_connected:
                    continue
                # Apply deadbands to the joystick
                forward = self.xbox_controller.LeftJoystickY if abs(self.xbox_controller.LeftJoystickY) > 0.15 else 0
                turn = self.xbox_controller.RightJoystickX if abs(self.xbox_controller.RightJoystickX) > 0.15 else 0
                lift = self.xbox_controller.RightJoystickY if abs(self.xbox_controller.RightJoystickY) > 0.15 else 0

                try:
                    # self.robot.get_state("/driv/cmd_vel").value = \
                    #     {"linear": {"x": forward, "y": 0, "z": 0}, "angular": {"x": 0, "y": 0, "z": turn}}
                    for quarter_module in modules:
                        self.robot.get_state(f"/mciu/{quarter_module}/odrive/input").value = [4, int(forward * 4000)]
                except Exception as e:
                    logging.error(f"Error writing to ROS: {e}")

                try:
                    self.robot.get_state("/driv/cmd_vel").value = \
                        {"linear": {"x": forward, "y": 0, "z": 0}, "angular": {"x": 0, "y": 0, "z": turn}}
                except Exception as e:
                    logging.error(f"Error writing to ROS: {e}")

                if self.xbox_controller.RightTrigger > -0.1 and self.xbox_controller.LeftTrigger > 0.6:
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

                if self.xbox_controller.Start or self.xbox_controller.Back:
                    try:
                        self.robot.get_state('/mciu/estop_controller').value = Enumerators.EStopCommands.TRIGGER
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")
            except Exception as e:
                logging.error(f"Error reading controller: {e}")

                time.sleep(5)

    # On resize adjust the positions of the widgets
    def resizeEvent(self, event):
        pass
