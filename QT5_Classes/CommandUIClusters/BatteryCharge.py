from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox


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

        self.add_charge_button = QPushButton("+1%", self)
        self.add_charge_button.setFixedSize(80, 25)
        self.add_charge_button.move(10, 20)
        self.add_charge_button.clicked.connect(self.increase_charge)
        self.add_charge_button.setDisabled(True)

        self.charge_button = QPushButton("Charge", self)
        self.charge_button.setFixedSize(80, 25)
        self.charge_button.move(100, 20)
        self.charge_button.clicked.connect(self.set_fully_charged)
        self.charge_button.setDisabled(True)

        self.del_charge_button = QPushButton("-1%", self)
        self.del_charge_button.setFixedSize(80, 25)
        self.del_charge_button.move(190, 20)
        self.del_charge_button.clicked.connect(self.decrease_charge)
        self.del_charge_button.setDisabled(True)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def set_fully_charged(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            confirm = ConfirmationBox(self, title="Confirm Battery Charge",
                                      message="Are you sure you want to mark the battery as fully charged?",
                                      detailed_message="This will reset the estimated battery charge to 100%,"
                                      " this action is irreversible and should only be run after each charge cycle.")

            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                logging.info("Sending command to set battery charge to 100%")
                self.robot.get_state('/mciu/battery_monitor').value = [0]
            else:
                logging.info("Operator cancelled the command to set battery charge to 100%")
        except Exception as e:
            logging.error(e)

    def increase_charge(self):
        try:
            self.robot.get_state('/mciu/battery_monitor').value = [1, 1]
        except Exception as e:
            logging.error(e)

    def decrease_charge(self):
        try:
            self.robot.get_state('/mciu/battery_monitor').value = [2, 1]
        except Exception as e:
            logging.error(e)

    def update(self):
        pass

    def on_robot_connection(self):
        self.add_charge_button.setDisabled(False)
        self.charge_button.setDisabled(False)
        self.del_charge_button.setDisabled(False)

    def on_robot_disconnection(self):
        self.add_charge_button.setDisabled(True)
        self.charge_button.setDisabled(True)
        self.del_charge_button.setDisabled(True)
