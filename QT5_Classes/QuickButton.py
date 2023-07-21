from PyQt5.QtWidgets import QPushButton


class QuickButton(QPushButton):
    """Sets up a standard button"""

    def __init__(self, text, parent=None, position=None, callback=None):
        super().__init__(text, parent)
        self.setFixedSize(80, 25)
        if position is not None:
            self.move(position[0], position[1])
        if callback is not None:
            self.clicked.connect(callback)
