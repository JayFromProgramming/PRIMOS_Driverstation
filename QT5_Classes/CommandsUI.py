from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QLabel

from QT5_Classes.CommandUIClusters.HopperControls import HopperDoorControls, HopperLoadSensors
from QT5_Classes.CommandUIClusters.MotorCalibControl import CalibrationCluster
from QT5_Classes.CommandUIClusters.SteeringModesCluster import SteeringModesCluster


class CommandsUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(830, 380)
        super().setFixedSize(830, 385)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: gray;")

        self.header = QLabel("Commands", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2), 0)

        self.steering_mode_cluster = SteeringModesCluster(self.robot, self)
        self.hopper_door_cluster = HopperDoorControls(self.robot, self)
        self.hopper_load_cluster = HopperLoadSensors(self.robot, self)
        self.calibration_cluster = CalibrationCluster(self.robot, self)

        self.steering_mode_cluster.move(10, 40)
        self.hopper_door_cluster.move(10, self.steering_mode_cluster.y() + self.steering_mode_cluster.height() + 5)
        self.hopper_load_cluster.move(10, self.hopper_door_cluster.y() + self.hopper_door_cluster.height() + 5)
        self.calibration_cluster.move(10, self.hopper_load_cluster.y() + self.hopper_load_cluster.height() + 5)

