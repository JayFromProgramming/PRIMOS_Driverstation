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

        # self.window.showMaximized()

        self.commands_ui = CommandsUI(self.robot, parent=self.window)
        self.window.resize(self.commands_ui.width(), self.commands_ui.height())

        self.commands_ui.move(0, 0)

        # Attach the resize event
        self.window.resizeEvent = self.resizeEvent
        self.window.show()

        threading.Thread(target=self.controller_read_loop).start()
        # multiprocessing.Process(target=self.controller_read_loop).start()

    # def run(self):
    #     """Draw the HUD until the program exits"""
    #
    #     with Live(self.draw_table(), refresh_per_second=1, screen=True) as live:
    #         while self.robot.client.is_connected:
    #             if self.should_redraw():
    #                 live.update(self.draw_table())
    #             time.sleep(0.1)

    def controller_read_loop(self):
        """Loop for the joystick"""
        modules = ["Front_Left", "Front_Right", "Rear_Left", "Rear_Right"]
        # Read the controller while the window is open
        while True:
            try:
                # Apply deadbands to the joystick
                forward = self.xbox_controller.LeftJoystickY * -0.6
                if abs(forward) > 0.05:
                    try:
                        self.robot.get_state(f"/mciu/Front_Left/odrive/input").value = [4, int((forward * 10000))]
                        self.robot.get_state(f"/mciu/Front_Right/odrive/input").value = [4, int((-forward * 10000))]
                        self.robot.get_state(f"/mciu/Rear_Left/odrive/input").value = [4, int((forward * 10000))]
                        self.robot.get_state(f"/mciu/Rear_Right/odrive/input").value = [4, int((-forward * 10000))]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")
                else:
                    try:
                        for quarter_modules in modules:
                            self.robot.get_state(f"/mciu/{quarter_modules}/odrive/input").value = [4, 0]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")
                turn = self.xbox_controller.LeftJoystickX * -1
                if abs(turn) < 0.15:
                    turn = 0

                if self.xbox_controller.B:
                    try:
                        for quarter_modules in modules:
                            self.robot.get_state(f"/mciu/{quarter_modules}/odrive/input").value = [0]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")
                elif self.xbox_controller.A:
                    try:
                        for quarter_modules in modules:
                            self.robot.get_state(f"/mciu/{quarter_modules}/odrive/input").value = [3, 2]
                    except Exception as e:
                        logging.error(f"Error writing to ROS: {e}")

                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Error reading controller: {e}")

                time.sleep(5)

    # On resize adjust the positions of the widgets
    def resizeEvent(self, event):
        pass

