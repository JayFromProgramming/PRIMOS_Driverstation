from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging


class SteeringModesCluster(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Set Steering Mode", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 15, 0)

        self.on_point_steering_button = QPushButton("Turn", self)
        self.on_point_steering_button.setFixedSize(80, 25)
        self.on_point_steering_button.move(10, 20)
        self.on_point_steering_button.clicked.connect(self.in_point_steering)
        self.on_point_steering_button.setEnabled(False)

        self.fused_steering_button = QPushButton("Drive", self)
        self.fused_steering_button.setFixedSize(80, 25)
        self.fused_steering_button.move(100, 20)
        self.fused_steering_button.clicked.connect(self.fused_steering)
        self.fused_steering_button.setEnabled(False)

        self.tank_steering_button = QPushButton("Parked", self)
        self.tank_steering_button.setFixedSize(80, 25)
        self.tank_steering_button.move(190, 20)
        self.tank_steering_button.clicked.connect(self.tank_steering)
        self.tank_steering_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connected)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnected)

    def in_point_steering(self):
        self.robot.execute_custom_service("steering_mode", "primos/switch_action", 1)

    def fused_steering(self):
        self.robot.execute_custom_service("steering_mode", "primos/switch_action", 2)

    def tank_steering(self):
        self.robot.execute_custom_service("steering_mode", "primos/switch_action", 3)

    def update(self):
        pass

    def on_robot_connected(self):
        self.on_point_steering_button.setEnabled(True)
        self.fused_steering_button.setEnabled(True)
        self.tank_steering_button.setEnabled(True)

    def on_robot_disconnected(self):
        self.on_point_steering_button.setEnabled(False)
        self.fused_steering_button.setEnabled(False)
        self.tank_steering_button.setEnabled(False)