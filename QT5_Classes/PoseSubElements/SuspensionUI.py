from PyQt5.QtWidgets import QWidget, QLabel


class SuspensionView(QWidget):

    def __init__(self, robot, side, mirrored=False, parent=None):
        super().__init__(parent)
        self.robot = robot

        # This widget draws the top down view of the drivetrain and displays the angle of the each wheel
        self.surface = QWidget(self)
        super().setFixedSize(250, 120)
        self.surface.setFixedSize(250, 120)

        self.mirrored = mirrored

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px;")
        self.header = QLabel(f"{side} Suspension View", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 14px; border: 0px; background-color: transparent;")
        self.header.move(round((self.width() - self.header.width()) / 2) - 20, 0)

        # Draw the wheels as circles and the linkages as lines

        self.wheel1 = QLabel(self.surface)
        self.wheel1.setStyleSheet("background-color: black; border-radius: 10px;")
        self.wheel1.setFixedSize(20, 20)
        # Move wheel 1 to the near bottom left corner of rover frame
        self.wheel1.move(40, 90)

        self.wheel2 = QLabel(self.surface)
        self.wheel2.setStyleSheet("background-color: black; border-radius: 10px;")
        self.wheel2.setFixedSize(20, 20)
        # Move wheel 2 to the near bottom right corner of rover frame
        self.wheel2.move(190, 90)

        # # Add the word "Front" to the right side of the view, the word should be written vertically
        # self.front = QLabel("Front", self.surface)
        # self.front.setStyleSheet("font-weight: bold; font-size: 14px; background-color: transparent;")
        # self.front.move(210, 40)
        # self.front
