from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging


class DriveTrainControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Drivetrain Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.enable_button = QPushButton("Enable", self)
        self.enable_button.setFixedSize(80, 25)
        self.enable_button.move(10, 20)
        self.enable_button.clicked.connect(self.open_door)
        self.enable_button.setEnabled(False)

        self.disable_button = QPushButton("Disable", self)
        self.disable_button.setFixedSize(80, 25)
        self.disable_button.move(100, 20)
        self.disable_button.clicked.connect(self.stop_door)
        self.disable_button.setEnabled(False)

        self.calibrate_button = QPushButton("Calibrate", self)
        self.calibrate_button.setFixedSize(80, 25)
        self.calibrate_button.move(190, 20)
        self.calibrate_button.clicked.connect(self.close_door)
        self.calibrate_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def on_robot_connection(self):
        self.enable_button.setEnabled(True)
        self.disable_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)

    def on_robot_disconnection(self):
        self.enable_button.setEnabled(False)
        self.disable_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)

    def open_door(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            self.robot.get_state('/mciu/Hopper/door').value = [2]
        except Exception as e:
            logging.error(e)

    def stop_door(self):
        try:
            self.robot.get_state('/mciu/Hopper/door').value = [1]
        except Exception as e:
            logging.error(e)

    def close_door(self):
        try:
            self.robot.get_state('/mciu/Hopper/door').value = [0]
        except Exception as e:
            logging.error(e)

    def update(self):
        pass
