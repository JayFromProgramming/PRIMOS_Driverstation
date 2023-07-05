from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

class AutomaticEStopControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Automatic E-Stop", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.enable_auto_button = QPushButton("Enable", self)
        self.enable_auto_button.setFixedSize(80, 25)
        self.enable_auto_button.move(10, 20)
        self.enable_auto_button.clicked.connect(self.enable_auto)
        self.enable_auto_button.setEnabled(False)

        self.reset_estop_button = QPushButton("Reset", self)
        self.reset_estop_button.setFixedSize(80, 25)
        self.reset_estop_button.move(100, 20)
        self.reset_estop_button.clicked.connect(self.reset_estop)
        self.reset_estop_button.setEnabled(False)

        self.disable_auto_button = QPushButton("Disable", self)
        self.disable_auto_button.setFixedSize(80, 25)
        self.disable_auto_button.move(190, 20)
        self.disable_auto_button.clicked.connect(self.disable_auto)
        self.disable_auto_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def reset_estop(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            self.robot.get_state('/mciu/estop_controller').value = 1
        except Exception as e:
            logging.error(e)

    def disable_auto(self):
        try:
            self.robot.get_state('/mciu/estop_controller').value = 3
        except Exception as e:
            logging.error(e)

    def enable_auto(self):
        try:
            self.robot.get_state('/mciu/estop_controller').value = 2
        except Exception as e:
            logging.error(e)

    def update(self):
        pass

    def on_robot_connection(self):
        self.enable_auto_button.setEnabled(True)
        self.reset_estop_button.setEnabled(True)
        self.disable_auto_button.setEnabled(True)

    def on_robot_disconnection(self):
        self.enable_auto_button.setEnabled(False)
        self.reset_estop_button.setEnabled(False)
        self.disable_auto_button.setEnabled(False)
