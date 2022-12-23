from PyQt5.QtWidgets import QWidget, QLabel


class TopDownUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        # This widget draws the top down view of the drivetrain and displays the angle of the each wheel
        self.surface = QWidget(self)
        self.surface.setFixedSize(140, 250)
        super().setFixedSize(140, 250)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px;")

        self.header = QLabel("Steering Angles", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 14px; border: 0px; background-color: transparent;")
        # self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2), 0)

        # Draw the wheels as rectangles and the linkages as lines
        self.wheel1 = QLabel(self.surface)
        self.wheel1.setStyleSheet("background-color: black;")
        self.wheel1.setFixedSize(20, 40)
        # Move wheel 1 to the top left corner of rover frame
        self.wheel1.move(20, 20)

        self.wheel2 = QLabel(self.surface)
        self.wheel2.setStyleSheet("background-color: black;")
        self.wheel2.setFixedSize(20, 40)
        # Move wheel 2 to the top right corner of rover frame
        self.wheel2.move(100, 20)

        self.wheel3 = QLabel(self.surface)
        self.wheel3.setStyleSheet("background-color: black;")
        self.wheel3.setFixedSize(20, 40)
        # Move wheel 3 to the bottom left corner of rover frame
        self.wheel3.move(20, 190)

        self.wheel4 = QLabel(self.surface)
        self.wheel4.setStyleSheet("background-color: black;")
        self.wheel4.setFixedSize(20, 40)
        self.wheel4.move(100, 190)
