import json

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget


class AnnunciatorIcon(QWidget):
    icon_gap_h = 5  # Horizontal gap between icons
    icon_gap_v = 10  # Vertical gap between icons

    def __init__(self, icon_file, mapping_info, size=(66, 41), parent=None):
        super().__init__(parent)
        self.ros_name = mapping_info["ros_name"]
        self.hover_text = mapping_info["hover_name"]
        self.location = mapping_info["annunciator_location"]
        self.icon = QtGui.QImage(icon_file)
        # Resize the icon to the desired size
        self.icon = self.icon.scaled(size[0], size[1], QtCore.Qt.KeepAspectRatio)
        self.setFixedSize(size[0], size[1])


class AnnunciatorUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__()
        super().setParent(parent)
        self.robot = robot
        self.parent = parent

        self.icons = {}
        self.icon_mappings = {}

        # Each icon is 66x41 pixels in size and there will be up to 5 icons per row and up to 3 rows
        # The icons will be placed in a grid layout with a 5 pixel gap between each icon and a 10 pixel
        # gap between each row

        self.icon_size = (round(66 * 1.5), round(41 * 1.5))

        self.icon_rows = 3
        self.icon_cols = 5
        self.icon_surface_size = (self.icon_size[0] * self.icon_cols +
                                  AnnunciatorIcon.icon_gap_h * (self.icon_cols - 1),
                                  self.icon_size[1] * self.icon_rows +
                                  AnnunciatorIcon.icon_gap_v * (self.icon_rows - 1))
        self.icon_surface = QWidget(parent=self)
        self.icon_surface.setFixedSize(*self.icon_surface_size)
        self.load_icons()

    def load_icons(self):
        # Icons are stored in the resources' folder under annunciator_icons
        self.icon_mappings = json.load(open("resources/annunciator_icons/icon_mappings.json"))
        for file_name, info in self.icon_mappings.items():
            # Build an icon object for each icon
            self.icons[info["ros_name"]] = \
                AnnunciatorIcon("resources/annunciator_icons/" + file_name, info, size=self.icon_size,
                                parent=self.icon_surface)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        for icon in self.icons.values():
            # Draw each icon in the correct location
            painter.drawImage(icon.location[0] * (self.icon_size[0] + AnnunciatorIcon.icon_gap_h),
                              icon.location[1] * (self.icon_size[1] + AnnunciatorIcon.icon_gap_v),
                              icon.icon)