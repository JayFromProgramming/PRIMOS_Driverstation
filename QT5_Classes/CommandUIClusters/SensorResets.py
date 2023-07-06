from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel


class SensorCalibrationCluster(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Sensor Calibrations", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.open_button = QPushButton("Hopper Tare", self)
        self.open_button.setFixedSize(80, 25)
        self.open_button.move(10, 20)
        self.open_button.clicked.connect(self.hopper)

        self.close_button = QPushButton("Suspen Tar", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(100, 20)
        self.close_button.clicked.connect(self.suspension)

        self.close_button = QPushButton("IMU Level", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(190, 20)
        self.close_button.clicked.connect(self.imu)

    def hopper(self):
        try:
            self.robot.get_state('/mciu/Hopper/loadcells/control').value = [0]
        except Exception as e:
            print(e)

    def suspension(self):
        try:
            self.robot.get_state('/mciu/Suspension/loadcells/control').value = [0]
        except Exception as e:
            print(e)

    def imu(self):
        try:
            self.robot.get_state('/mciu/IMU/level').value = [0]
        except Exception as e:
            print(e)

    def update(self):
        pass