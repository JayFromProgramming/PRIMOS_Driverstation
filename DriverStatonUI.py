import multiprocessing
import time
import threading

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

import controller
from QT5_Classes.AnnunciatorUI import AnnunciatorUI
# from QT5_Classes.CannonUI import CannonUI
# from QT5_Classes.ConnectionUI import ConnectionUI
# from QT5_Classes.PointCloud2UI import PointCloud2UI
# from QT5_Classes.SignalUI import SignalUI
# from QT5_Classes.PioneerUI import PioneerUI
# from QT5_Classes.TopicStatusUI import TopicUI
# from QT5_Classes.WebcamUI import WebcamWindow
from QT5_Classes.BatteryUI import BatteryUI
from QT5_Classes.CommandsUI import CommandsUI
from QT5_Classes.DataLoggingUI import DataLoggingUI
from QT5_Classes.HopperUI import HopperUI
from QT5_Classes.MotorStateUI import MotorStateUI
from QT5_Classes.PoseUI import PoseUI
from ROS.ROSInterface import ROSInterface
from ROS.RobotState import RobotState

import logging

logging = logging.getLogger(__name__)


class DriverStationUI:

    def __init__(self, robot: ROSInterface):

        self.robot = robot
        self.last_redraw = 0  # type: int

        self.robot_state = robot.robot_state_monitor.state_watcher  # type: RobotState
        try:
            self.xbox_controller = controller.XboxController()
        except Exception as e:
            logging.error(f"Error initializing controller: {e}")
            self.xbox_controller = None

        self.window = QMainWindow()
        self.window.resize(1920, 1080)

        self.annunciator_ui = AnnunciatorUI(self.robot, parent=self.window)
        self.battery_ui = BatteryUI(self.robot, parent=self.window)
        self.motor_overview = MotorStateUI(self.robot, parent=self.window)
        self.pose_ui = PoseUI(self.robot, parent=self.window)
        self.commands_ui = CommandsUI(self.robot, parent=self.window)
        self.hopper_ui = HopperUI(self.robot, parent=self.window)
        self.data_logging_ui = DataLoggingUI(self.robot, parent=self.window)

        self.motor_overview.move(5, self.window.height() - self.motor_overview.height() - 5)
        self.annunciator_ui.move(5, self.motor_overview.y() - self.annunciator_ui.height() - 5)
        self.battery_ui.move(self.annunciator_ui.x() + self.annunciator_ui.width() + 5, self.annunciator_ui.y())
        self.pose_ui.move(5, self.annunciator_ui.y() - self.pose_ui.height() - 5)

        self.commands_ui.move(self.window.width() - self.commands_ui.width() - 5,
                              self.window.height() - self.commands_ui.height() - 5)

        self.hopper_ui.move(self.commands_ui.x(), self.commands_ui.y() - self.hopper_ui.height() - 5)
        self.data_logging_ui.move(self.hopper_ui.x() + self.data_logging_ui.width() + 5, self.hopper_ui.y())

        # self.topic_info = TopicUI(self.robot, self.window)

        # Attach the resize event
        self.window.resizeEvent = self.resizeEvent
        self.window.show()

        # threading.Thread(target=self.controller_read_loop).start()
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
        # Read the controller while the window is open
        try:
            while True:
                # Apply deadbands to the joystick
                forward = self.xbox_controller.LeftJoystickY * -1
                if abs(forward) < 0.15:
                    forward = 0
                turn = self.xbox_controller.LeftJoystickX * -1
                if abs(turn) < 0.15:
                    turn = 0

                self.robot.drive(forward, turn)

                if self.xbox_controller.A:
                    self.robot.execute_service("my_p3at/enable_motors")
                if self.xbox_controller.B:
                    self.robot.execute_service("my_p3at/disable_motors")
                if self.xbox_controller.X:
                    self.sonar_view.toggle()
                if self.xbox_controller.Y:
                    self.robot.execute_service("/can/fire")

                if self.xbox_controller.LeftBumper:
                    if not self.cannon_ui.tank1.cannonArmed():
                        self.cannon_ui.tank1.armDisarm(True)
                        self.tank1_was_armed = True
                else:
                    if self.cannon_ui.tank1.cannonArmed() and self.tank1_was_armed:
                        self.cannon_ui.tank1.armDisarm(False)
                        self.tank1_was_armed = False

                if self.xbox_controller.RightBumper:
                    if not self.cannon_ui.tank2.cannonArmed():
                        self.cannon_ui.tank2.armDisarm(True)
                        self.tank2_was_armed = True
                else:
                    if self.cannon_ui.tank2.cannonArmed() and self.tank2_was_armed:
                        self.cannon_ui.tank2.armDisarm(False)
                        self.tank2_was_armed = False

                time.sleep(0.1)
        except Exception as e:
            logging.error(f"Error reading controller: {e}")
            self.robot.drive(0, 0)

    # On resize adjust the positions of the widgets
    def resizeEvent(self, event):
        self.motor_overview.move(5, self.window.height() - self.motor_overview.height() - 5)
        self.annunciator_ui.move(5, self.motor_overview.y() - self.annunciator_ui.height() - 5)
        self.battery_ui.move(self.annunciator_ui.x() + self.annunciator_ui.width() + 5, self.annunciator_ui.y())
        self.pose_ui.move(5, self.annunciator_ui.y() - self.pose_ui.height() - 5)

        self.commands_ui.move(self.window.width() - self.commands_ui.width() - 5,
                              self.window.height() - self.commands_ui.height() - 5)
