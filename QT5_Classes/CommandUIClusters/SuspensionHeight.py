from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel


class SuspensionHeight(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Suspension Height", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.auto_button = QPushButton("Auto", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.increase_charge)
        self.auto_button.setDisabled(True)

        self.manual_button = QPushButton("Manual", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.set_fully_charged)
        self.manual_button.setDisabled(True)

        self.maximum_button = QPushButton("Maximum", self)
        self.maximum_button.setFixedSize(80, 25)
        self.maximum_button.move(190, 20)
        self.maximum_button.clicked.connect(self.decrease_charge)
        self.maximum_button.setDisabled(True)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

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

    def on_robot_connection(self):
        self.auto_button.setDisabled(False)
        self.manual_button.setDisabled(False)
        self.maximum_button.setDisabled(False)

    def on_robot_disconnection(self):
        self.auto_button.setDisabled(True)
        self.manual_button.setDisabled(True)
        self.maximum_button.setDisabled(True)

