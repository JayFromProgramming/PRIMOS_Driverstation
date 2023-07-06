from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ErrorBox import ErrorBox


class LaserPowerControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Laser Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.turn_on_button = QPushButton("Turn On", self)
        self.turn_on_button.setFixedSize(125, 25)
        self.turn_on_button.move(10, 20)
        self.turn_on_button.clicked.connect(self.on)
        self.turn_on_button.setEnabled(False)

        self.turn_off_button = QPushButton("Turn Off", self)
        self.turn_off_button.setFixedSize(125, 25)
        self.turn_off_button.move(145, 20)
        self.turn_off_button.clicked.connect(self.off)
        self.turn_off_button.setEnabled(False)

        # self.close_button = QPushButton("-5%", self)
        # self.close_button.setFixedSize(80, 25)
        # self.close_button.move(190, 20)
        # self.close_button.clicked.connect(self.decrease_charge)

        self.robot.attach_on_connect_callback(self.on_robot_connected)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnected)

    def on_robot_connected(self):
        self.turn_on_button.setEnabled(True)
        self.turn_off_button.setEnabled(True)

    def on_robot_disconnected(self):
        self.turn_on_button.setEnabled(False)
        self.turn_off_button.setEnabled(False)

    def on(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            self.robot.get_state('/mciu/accessory_power').value = [0, 1]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Internal Error", message="Unable to command laser power on", error=e)

    def off(self):
        try:
            self.robot.get_state('/mciu/accessory_power').value = [0, 0]
        except Exception as e:
            ErrorBox(self, title="Internal Error", message="Unable to command laser power off", error=e)

    def update(self):
        pass

