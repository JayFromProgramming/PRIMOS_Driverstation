from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QLabel


class PoseUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.battery = self.robot.get_state("battery_state")

        self.surface = QWidget(self)
        self.surface.setFixedSize(1070, 304)
        super().setFixedSize(1070, 304)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: gray;")

        self.header = QLabel("Rover Pose", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px; "
                                          "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2), 0)
