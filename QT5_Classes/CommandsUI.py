from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QLabel

from QT5_Classes.CommandUIClusters.BatteryCharge import BatteryCharge
from QT5_Classes.CommandUIClusters.EStopButton import EStopButton
from QT5_Classes.CommandUIClusters.EStopControls import AutomaticEStopControls
from QT5_Classes.CommandUIClusters.HopperControls import HopperDoorControls, HopperLoadSensors
from QT5_Classes.CommandUIClusters.MotorCalibControl import MotorCalibrationCluster
from QT5_Classes.CommandUIClusters.SensorResets import SensorCalibrationCluster
from QT5_Classes.CommandUIClusters.SteeringModesCluster import SteeringModesCluster
from QT5_Classes.CommandUIClusters.TrencherControls import TrencherControls


class CommandsUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(870, 380)
        super().setFixedSize(870, 380)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: gray;")

        self.header = QLabel("Commands", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2), 0)

        self.steering_mode_cluster = SteeringModesCluster(self.robot, self)
        self.hopper_door_cluster = HopperDoorControls(self.robot, self)
        self.hopper_load_cluster = HopperLoadSensors(self.robot, self)
        self.motor_calibration_cluster = MotorCalibrationCluster(self.robot, self)
        # self.sensor_calibration_cluster = SensorCalibrationCluster(self.robot, self)
        self.auto_estop_controls = AutomaticEStopControls(self.robot, self)
        self.estop_button = EStopButton(self.robot, self)
        self.trencher = TrencherControls(self.robot, self)
        self.battery = BatteryCharge(self.robot, self)

        # Column 1
        self.steering_mode_cluster.move(10, 40)
        self.hopper_door_cluster.move(10, self.steering_mode_cluster.y() + self.steering_mode_cluster.height() + 5)
        self.hopper_load_cluster.move(10, self.hopper_door_cluster.y() + self.hopper_door_cluster.height() + 5)
        self.motor_calibration_cluster.move(10, self.hopper_load_cluster.y() + self.hopper_load_cluster.height() + 5)
        # self.sensor_calibration_cluster.move(10, self.motor_calibration_cluster.y() +
        #                                      self.motor_calibration_cluster.height() + 5)

        # Column 2
        self.auto_estop_controls.move(self.steering_mode_cluster.x() + self.steering_mode_cluster.width() + 5, 40)
        self.estop_button.move(self.auto_estop_controls.x(),
                               self.auto_estop_controls.y() + self.auto_estop_controls.height() + 5)
        self.trencher.move(self.auto_estop_controls.x(),
                           self.estop_button.y() + self.estop_button.height() + 5)

        # Column 3
        self.battery.move(self.auto_estop_controls.x() + self.auto_estop_controls.width() + 5, 40)
