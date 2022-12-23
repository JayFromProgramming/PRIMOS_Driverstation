from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QLabel

from QT5_Classes.PoseSubElements.SuspensionUI import SuspensionView
from QT5_Classes.PoseSubElements.TopDownUI import TopDownUI


class PoseUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.pose = self.robot.get_state("pose")

        self.surface = QWidget(self)
        self.surface.setFixedSize(1070, 304)
        super().setFixedSize(1070, 304)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: gray;")

        self.header = QLabel("Rover Pose", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2), 0)

        self.topDown = TopDownUI(self.robot, self.surface)
        # Move the top down view to the right side of the rover pose widget
        self.topDown.move(self.width() - self.topDown.width() - 10,
                            round(self.height() / 2 - self.topDown.height() / 2))

        self.suspension_left = SuspensionView(self.robot, "Left", True, self.surface)
        self.suspension_right = SuspensionView(self.robot, "Right", False, self.surface)

        # The suspension views are places to the left of the top down view and are stacked on top of each other
        self.suspension_left.move(self.topDown.x() - self.suspension_left.width() - 10,
                                      round(self.height() / 2 - self.suspension_right.height() - 5))
        self.suspension_right.move(self.topDown.x() - self.suspension_right.width() - 10,
                                        round(self.height() / 2 + 5))

