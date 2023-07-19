from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QLabel

from QT5_Classes.CommandUIClusters.BatteryCharge import BatteryCharge
from QT5_Classes.CommandUIClusters.ControllerConnectionUI import ControllerConnectionUI, ControllerMappingUI
from QT5_Classes.CommandUIClusters.ConveyorControls import ConveyorControls
from QT5_Classes.CommandUIClusters.DrivetrainControls import DriveTrainControls
from QT5_Classes.CommandUIClusters.EStopButton import EStopButton
from QT5_Classes.CommandUIClusters.EStopControls import AutomaticEStopControls
from QT5_Classes.CommandUIClusters.HopperControls import HopperDoorControls, HopperLoadSensors
from QT5_Classes.CommandUIClusters.JetsonSSHControls import JetsonControls
from QT5_Classes.CommandUIClusters.AccessoryPowerControls import AccessoryPowerControls
from QT5_Classes.CommandUIClusters.MotorCalibControl import MotorCalibrationCluster
from QT5_Classes.CommandUIClusters.RosbagControls import RosbagControls
from QT5_Classes.CommandUIClusters.RoverConnectionUI import RoverConnectionUI
from QT5_Classes.CommandUIClusters.SensorResets import SensorCalibrationCluster
from QT5_Classes.CommandUIClusters.SteeringModesCluster import SteeringModesCluster
from QT5_Classes.CommandUIClusters.SuspensionModeSelect import SuspensionModeSelect
from QT5_Classes.CommandUIClusters.TrencherControls import TrencherControls


class CommandsUI(QWidget):

    def __init__(self, robot, parent=None, xbox_controller=None):
        super().__init__(parent)
        self.robot = robot
        self.xbox_controller = xbox_controller

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
        # self.motor_calibration_cluster = MotorCalibrationCluster(self.robot, self)
        # self.sensor_calibration_cluster = SensorCalibrationCluster(self.robot, self)
        self.auto_estop_controls = AutomaticEStopControls(self.robot, self)
        self.estop_button = EStopButton(self.robot, self)
        self.connection_status = RoverConnectionUI(self.robot, self)
        self.controller_status = ControllerConnectionUI(self.robot, self, self.xbox_controller)
        # self.controller_mapping = ControllerMappingUI(self.robot, self, self.xbox_controller)
        self.trencher = TrencherControls(self.robot, self)
        self.conveyor = ConveyorControls(self.robot, self)
        self.battery = BatteryCharge(self.robot, self)
        self.laser_power = AccessoryPowerControls(self.robot, self, target_name="Laser", target_id=0)
        self.camera_power = AccessoryPowerControls(self.robot, self, target_name="Camera", target_id=1)
        self.drivetrain = DriveTrainControls(self.robot, self)
        self.suspension = SuspensionModeSelect(self.robot, self, self.xbox_controller)
        self.jetson = JetsonControls(self.robot, self)
        self.rosbag = RosbagControls(self.robot, self)

        # Column 1
        self.hopper_door_cluster.move(10, 40)
        self.drivetrain.move(self.hopper_door_cluster.x(),
                             self.hopper_door_cluster.y() + self.hopper_door_cluster.height() + 5)
        self.steering_mode_cluster.move(self.drivetrain.x(),
                                        self.drivetrain.y() + self.drivetrain.height() + 5)
        self.suspension.moved(self.drivetrain.x(), self.steering_mode_cluster.y() + self.steering_mode_cluster.height() + 5)

        # Column 2
        self.auto_estop_controls.move(self.steering_mode_cluster.x() + self.steering_mode_cluster.width() + 5, 40)
        self.estop_button.move(self.auto_estop_controls.x(),
                               self.auto_estop_controls.y() + self.auto_estop_controls.height() + 5)
        self.connection_status.move(self.auto_estop_controls.x(),
                                    self.estop_button.y() + self.estop_button.height() + 5)
        self.controller_status.move(self.auto_estop_controls.x(),
                                    self.connection_status.y() + self.connection_status.height() + 5)
        self.rosbag.move(self.auto_estop_controls.x(),
                         self.controller_status.y() + self.controller_status.height() + 5)
        self.jetson.move(self.auto_estop_controls.x(), self.rosbag.y() + self.rosbag.height() + 5)

        # Column 3
        self.battery.move(self.auto_estop_controls.x() + self.auto_estop_controls.width() + 5, 40)
        self.laser_power.move(self.battery.x(), self.battery.y() + self.battery.height() + 5)
        self.camera_power.move(self.battery.x(), self.laser_power.y() + self.laser_power.height() + 5)
        self.hopper_load_cluster.move(self.battery.x(), self.camera_power.y() + self.camera_power.height() + 5)
        self.trencher.move(self.battery.x(), self.hopper_load_cluster.y() + self.hopper_load_cluster.height() + 5)
        self.conveyor.move(self.battery.x(), self.trencher.y() + self.trencher.height() + 5)

