from PyQt5 import Qt


class ConfirmationBox(Qt.QMessageBox):

    def __init__(self, parent=None, title=None, message=None, detailed_message=None):
        super().__init__(parent)

        self.setText(message)
        self.setDetailedText(detailed_message)
        self.setStandardButtons(Qt.QMessageBox.Yes | Qt.QMessageBox.No)
        self.setDefaultButton(Qt.QMessageBox.No)
        self.setWindowTitle(title)
        # self.setFixedSize(500, 200)
