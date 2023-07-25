from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ErrorBox import ErrorBox


class TrencherControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Trencher Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.arm_button = QPushButton("Arm", self)
        self.arm_button.setFixedSize(125, 25)
        self.arm_button.move(10, 20)
        self.arm_button.clicked.connect(self.arm)
        self.arm_button.setEnabled(False)

        self.disarm_button = QPushButton("Disarm", self)
        self.disarm_button.setFixedSize(125, 25)
        self.disarm_button.move(145, 20)
        self.disarm_button.clicked.connect(self.disarm)
        self.disarm_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connected)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnected)

    def on_robot_connected(self):
        self.arm_button.setEnabled(True)
        self.disarm_button.setEnabled(True)

    def on_robot_disconnected(self):
        self.arm_button.setEnabled(False)
        self.disarm_button.setEnabled(False)

    def arm(self):
        try:
            # self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
            self.robot.get_state("/mciu/Trencher/odrive/input").value = [3, 2, 2]
            self.robot.get_state("/mciu/Conveyor/odrive/input").value = [3, 2, 1]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Could not arm trencher.", error=e)

    def disarm(self):
        try:
            # self.robot.execute_custom_service("/trch/arm", {"in_": False}, "primrose_trch/set_armed")
            self.robot.get_state("/mciu/Trencher/odrive/input").value = [1]
            self.robot.get_state("/mciu/Conveyor/odrive/input").value = [1]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Could not disarm trencher.", error=e)

    def update(self):
        pass

