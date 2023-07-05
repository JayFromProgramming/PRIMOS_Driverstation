from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel


class BatteryCharge(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Battery Charge", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.open_button = QPushButton("+5%", self)
        self.open_button.setFixedSize(80, 25)
        self.open_button.move(10, 20)
        self.open_button.clicked.connect(self.increase_charge)

        self.close_button = QPushButton("Charge", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(100, 20)
        self.close_button.clicked.connect(self.set_fully_charged)

        self.close_button = QPushButton("-5%", self)
        self.close_button.setFixedSize(80, 25)
        self.close_button.move(190, 20)
        self.close_button.clicked.connect(self.decrease_charge)

    def set_fully_charged(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            self.robot.get_state('/mciu/battery_monitor').value = 1
        except Exception as e:
            print(e)

    def increase_charge(self):
        try:
            self.robot.get_state('/mciu/battery_monitor').value = 3
        except Exception as e:
            print(e)

    def decrease_charge(self):
        try:
            self.robot.get_state('/mciu/battery_monitor').value = 2
        except Exception as e:
            print(e)

    def update(self):
        pass

