from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ErrorBox import ErrorBox


class ConveyorControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Conveyor Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.auto_button = QPushButton("Auto", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.auto)
        self.auto_button.setEnabled(False)

        self.manual_button = QPushButton("Manual", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.manual)
        self.manual_button.setEnabled(False)

        self.disable_button = QPushButton("Disable", self)
        self.disable_button.setFixedSize(80, 25)
        self.disable_button.move(190, 20)
        self.disable_button.clicked.connect(self.disabled)
        self.disable_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connected)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnected)

    def on_robot_connected(self):
        self.auto_button.setEnabled(True)
        self.manual_button.setEnabled(True)
        self.disable_button.setEnabled(True)

    def on_robot_disconnected(self):
        self.auto_button.setEnabled(False)
        self.manual_button.setEnabled(False)
        self.disable_button.setEnabled(False)

    def auto(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_conv/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Could not change conveyor state.", error=e)

    def manual(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": False}, "primrose_conv/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Could not change conveyor state.", error=e)

    def disabled(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": False}, "primrose_conv/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Could not change conveyor state.", error=e)

    def update(self):
        pass

