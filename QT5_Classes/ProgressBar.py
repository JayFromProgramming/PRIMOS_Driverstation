from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QProgressBar

from loguru import logger as logging

class ProgressBar(QMessageBox):
    """
    Contains a simple progress bar that can be updated as needed without blocking execution.
    """

    def __init__(self, parent=None, title="Progress", message="Progress", detailed_message=None, max_value=100,
                 cancelable=False, cancel_callback=None):
        super(ProgressBar, self).__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(message)
        if cancelable:
            self.setStandardButtons(QMessageBox.Cancel)
            self.buttonClicked.connect(cancel_callback)
        else:
            self.setStandardButtons(QMessageBox.NoButton)
        if detailed_message is not None:
            self.setDetailedText(detailed_message)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, max_value)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedSize(300, 25)
        # self.progress_bar.move(10, 50)

        self.setFixedSize(600, 300)
        logging.info("Progress bar created")
        self.repaint()
        # Display the modal without blocking execution of the program
        self.show()

    def set_progress(self, value, new_message=None):
        """
        Sets the progress bar value to the specified value.
        :param value: The value to set the progress bar to.
        :return: None
        """
        logging.info(f"Setting progress bar to {value}")
        self.progress_bar.setValue(value)
        if new_message is not None:
            self.setText(new_message)
        # self.repaint()
