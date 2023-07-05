from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel


class EStopButton(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        # self.header = QLabel("Automatic Estop", self.surface)
        # self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
        #                           "background-color: transparent;")
        # self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.estop_button = QPushButton("ESTOP", self)
        self.estop_button.setStyleSheet(
            "background-color: red; border: 1px solid black; border-radius: 5px; font-weight: bold; font-size: 15px;"
        )
        self.estop_button.setFixedSize(260, 40)
        self.estop_button.move(10, 5)
        self.estop_button.clicked.connect(self.estop)

    def estop(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            self.robot.get_state('/mciu/estop_controller').value = 0
        except Exception as e:
            print(e)

    def update(self):
        pass

