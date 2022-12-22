import json
import logging
import os
import random
import traceback

from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QLabel

from QT5_Classes.ODriveMotor import ODriveMotor


class MotorStateUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__()
        super().setParent(parent)
        super().setFixedSize(1070, 385)
        self.robot = robot
        self.parent = parent

        self.info_topic = self.robot.get_state("motor_state_info")  # type RobotState.SmartTopic

        self.surface = QWidget(self)
        self.surface.setFixedSize(1070, 380)

        self.motor_state_labels = []
        self.motor_state_header = QLabel("Motors", self.surface)

        self.motor_state_header.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px; "
                                              "background-color: transparent;")
        self.motor_state_header.setAlignment(Qt.Qt.AlignCenter)
        self.motor_state_header.move(round(self.width() / 2 - self.motor_state_header.width() / 2), 0)
        self.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: gray;")

        if os.path.exists("configs/motors.json"):
            with open("configs/motors.json", "r") as f:
                motors = json.load(f)
        else:
            motors = {}
            with open("configs/motors.json", "w") as f:
                json.dump(motors, f)

        for name, info in motors.items():
            if info["type"] == "odrive":
                motor = ODriveMotor(info["screen_name"], name, self.surface)
                motor.move(5 + (info["pos"][0] * 355),
                           40 + (info["pos"][1] * 55))
                self.motor_state_labels.append(motor)

        # Setup the timer to update the labels
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_loop)
        self.update_timer.start(250)

    def update_loop(self):
        for motor in self.motor_state_labels:
            try:
                motor.update(speed=random.randint(-1000, 1000), current=random.randint(0, 25),
                             motor_temp=random.randint(0, 100), fet_temp=random.randint(0, 100))
            except Exception as e:
                logging.error(f"motor_state_ui: {e}\n{traceback.format_exc()}")

