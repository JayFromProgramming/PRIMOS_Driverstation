from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ErrorBox import ErrorBox


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

        def on_success(response):
            self.on_point_steering_button.setEnabled(True)

        def on_failure(error):
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=error)
            self.on_point_steering_button.setEnabled(True)

        try:
            self.robot.execute_custom_service("/", {"in_": True}, "primrose_trch/set_armed",
                                              callback=on_success, errback=on_failure)
            self.on_point_steering_button.setEnabled(False)
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=e)
            self.on_point_steering_button.setEnabled(True)

    def fused_steering(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=e)

    def tank_steering(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=e)

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