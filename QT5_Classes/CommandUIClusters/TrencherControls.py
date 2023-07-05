from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel


class TrencherControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Trencher Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.open_button = QPushButton("Arm", self)
        self.open_button.setFixedSize(125, 25)
        self.open_button.move(10, 20)
        self.open_button.clicked.connect(self.arm)

        self.close_button = QPushButton("Disarm", self)
        self.close_button.setFixedSize(125, 25)
        self.close_button.move(145, 20)
        self.close_button.clicked.connect(self.disarm)

        # self.close_button = QPushButton("InOp", self)
        # self.close_button.setFixedSize(80, 25)
        # self.close_button.move(190, 20)
        # self.close_button.clicked.connect(self.imu)

    def arm(self):
        self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        try:
            self.robot.get_state("/mciu/Trencher/odrive/input").value = [3, 2, 2]
            self.robot.get_state("/mciu/Conveyor/odrive/input").value = [3, 2, 2]
        except Exception as e:
            print(e)

    def disarm(self):
        self.robot.execute_custom_service("/trch/arm", {"in_": False}, "primrose_trch/set_armed")
        try:
            self.robot.get_state("/mciu/Trencher/odrive/input").value = [0]
            self.robot.get_state("/mciu/Conveyor/odrive/input").value = [0]
        except Exception as e:
            print(e)

    def update(self):
        pass

