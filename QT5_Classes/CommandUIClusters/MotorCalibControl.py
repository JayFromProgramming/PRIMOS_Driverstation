from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

modules = ["Front_Left", "Front_Right", "Rear_Left", "Rear_Right"]


class MotorCalibrationCluster(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Motor Calibrations", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.open_button = QPushButton("Motors", self)
        self.open_button.setFixedSize(80, 25)
        self.open_button.move(10, 20)
        self.open_button.clicked.connect(self.motors)

        self.close_button = QPushButton("Suspension", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(100, 20)
        self.close_button.clicked.connect(self.suspension)

        self.close_button = QPushButton("Steering", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(190, 20)
        self.close_button.clicked.connect(self.steering)

    def motors(self):
        try:

            for quarter_module in modules:
                self.robot.get_state(f"/mciu/{quarter_module}/odrive/input").value = [2]

            for quarter_module in modules:
                self.robot.get_state(f"/mciu/{quarter_module}/odrive/input").value = [3, 2]

            # for quarter_module in modules:
            #     self.robot.get_state(f"/mciu/{quarter_module}/odrive/input").value = [4, int(16900 * 2/3)]

        except Exception as e:
            print(e)

    def suspension(self):
        try:
            for quarter_module in modules:
                self.robot.get_state(f"/mciu/{quarter_module}/odrive/input").value = [0]
        except Exception as e:
            print(e)

    def steering(self):
        try:
            print(f"Homing steering motors...")
            for quarter_module in modules:
                self.robot.get_state(f"/mciu/{quarter_module}/actuators/input").value = [3, 1]
        except Exception as e:
            print(e)

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

        self.header = QLabel("Weight Sensors", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 10, 0)

        self.tare_button = QPushButton("Tare", self)
        self.tare_button.setFixedSize(80, 25)
        self.tare_button.move(10, 20)
        self.tare_button.clicked.connect(self.tare_sensors)

        self.tare_button = QPushButton("Shake", self)
        self.tare_button.setFixedSize(80, 25)
        self.tare_button.move(100, 20)
        self.tare_button.clicked.connect(self.shake_sensors)

        self.tare_button = QPushButton("InOp", self)
        self.tare_button.setFixedSize(80, 25)
        self.tare_button.move(190, 20)

    def tare_sensors(self):
        self.robot.execute_service("hopper_tare_sensors")

    def shake_sensors(self):
        self.robot.execute_service("hopper_shake_sensors")
