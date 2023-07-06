from PyQt5.QtWidgets import QMessageBox


class ErrorBox(QMessageBox):
    def __init__(self, parent=None, title="Internal Error", message="Error", detailed_message=None, error=None):
        super(ErrorBox, self).__init__(parent)
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle(title)
        self.setText(message)
        # If the error has been passed then use traceback to format the error
        if error is not None:
            import traceback
            self.setInformativeText(f"{type(error).__name__}\n{error}")
            self.setDetailedText(traceback.format_exc())
        if detailed_message is not None:
            self.setInformativeText(detailed_message)
        self.setStandardButtons(QMessageBox.Ok)
        self.exec_()