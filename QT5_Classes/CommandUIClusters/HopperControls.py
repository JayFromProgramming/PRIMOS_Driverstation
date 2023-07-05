from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

class HopperDoorControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Hopper Door", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.open_button = QPushButton("Open", self)
        self.open_button.setFixedSize(80, 25)
        self.open_button.move(10, 20)
        self.open_button.clicked.connect(self.open_door)

        self.close_button = QPushButton("Stop", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(100, 20)
        self.close_button.clicked.connect(self.stop_door)

        self.close_button = QPushButton("Close", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(190, 20)
        self.close_button.clicked.connect(self.close_door)

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


class HopperLoadSensors(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Load Cell Resets", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 10, 0)

        self.tare_button = QPushButton("Hopper Tare", self)
        self.tare_button.setFixedSize(125, 25)
        self.tare_button.move(10, 20)
        self.tare_button.clicked.connect(self.tare_hopper)

        self.tare_button = QPushButton("Suspension Tar", self)
        self.tare_button.setFixedSize(125, 25)
        self.tare_button.move(145, 20)
        self.tare_button.clicked.connect(self.tare_suspension)

        # self.tare_button = QPushButton("InOp", self)
        # self.tare_button.setFixedSize(80, 25)
        # self.tare_button.move(190, 20)

    def tare_hopper(self):
        try:
            self.robot.get_state('/mciu/Hopper/loadcells/control').value = [1]
        except Exception as e:
            logging.error(e)

    def tare_suspension(self):
        try:
            self.robot.get_state('/mciu/Suspension/loadcells/control').value = [1]
        except Exception as e:
            logging.error(e)
