import json
import logging
import os
import threading
import multiprocessing

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget


class AnnunciatorIcon(QWidget):
    icon_gap_h = 5  # Horizontal gap between icons
    icon_gap_v = 5  # Vertical gap between icons

    def __init__(self, icon_file, mapping_info, size=(66, 41), parent=None):
        super().__init__(parent)
        self.ros_name = mapping_info["ros_name"]
        self.hover_text = mapping_info["hover_name"]
        raw_location = mapping_info["annunciator_location"]
        x = raw_location[1] * (size[0] + AnnunciatorIcon.icon_gap_h) + AnnunciatorIcon.icon_gap_h
        y = raw_location[0] * (size[1] + AnnunciatorIcon.icon_gap_v) + AnnunciatorIcon.icon_gap_v
        self.setGeometry(x, y, size[0], size[1])

        self.icon = None
        self.icons = {  # Instead of change the color of the icon each time we cache them and switch between them
            "red": None,
            "orange": None,
            "green": None,
            "gray": None
        }

        base_icon = QtGui.QImage(icon_file)
        if mapping_info["auto_crop"]:
            base_icon = base_icon.copy(self.auto_crop(base_icon))

        self.icon_offset_x = 0
        self.icon_offset_y = 0

        # Resize the icon to the desired size
        self.build_thread = threading.Thread(target=self.build_icon, args=(base_icon, size))

        # Check if the icons are already cached
        self.built = False
        for color in self.icons:
            if os.path.isfile("cache/tell_tails/" + self.ros_name + "_" + color + ".png"):
                self.icons[color] = QtGui.QImage("cache/tell_tails/" + self.ros_name + "_" + color + ".png")
                self.icon_offset_x = (size[0] - self.icons[color].width()) // 2
                self.icon_offset_y = (size[1] - self.icons[color].height()) // 2
            else:
                self.built = False
                break
        else:
            self.built = True
            self.scale_icons(size)

        self.updated = False

        self.selected_color = "red"
        self.display_color = "red"
        self.blink = True  # Blink the icon between the selected color and gray (does not work with the gray color)

        # Remove the alpha channel
        # self.icon = self.icon.convertToFormat(QtGui.QImage.Format_RGB888)
        self.setFixedSize(size[0], size[1])

    def build_icon(self, base_icon, size):
        self.built = True
        self.generate_icons(base_icon)
        self.scale_icons(size)
        self.updated = True

    @staticmethod
    def auto_crop(image):
        # Find the first non-transparent pixel for each side to auto crop the image
        x1, y1, x2, y2 = 0, 0, image.width(), image.height()
        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixelColor(x, y).alpha() != 0:
                    x1 = x
                    break
            else:
                continue
            break
        for x in range(image.width() - 1, -1, -1):
            for y in range(image.height()):
                if image.pixelColor(x, y).alpha() != 0:
                    x2 = x
                    break
            else:
                continue
            break
        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixelColor(x, y).alpha() != 0:
                    y1 = y
                    break
            else:
                continue
            break
        for y in range(image.height() - 1, -1, -1):
            for x in range(image.width()):
                if image.pixelColor(x, y).alpha() != 0:
                    y2 = y
                    break
            else:
                continue
            break
        return QtCore.QRect(x1, y1, x2 - x1, y2 - y1)

    def generate_icons(self, base_icon):
        # We need to convert the image to a gray scale image (preserving the alpha channel)
        gray_image = QtGui.QImage(base_icon.size(), QtGui.QImage.Format_ARGB32)
        for x in range(base_icon.width()):
            for y in range(base_icon.height()):
                color = base_icon.pixelColor(x, y)
                gray = (color.red() + color.green() + color.blue()) // 3
                gray_image.setPixelColor(x, y, QtGui.QColor(gray, gray, gray, color.alpha()))

        # Generate the colored icons by replacing the gray pixels with the desired color
        for color in self.icons:
            self.icons[color] = QtGui.QImage(base_icon)
            for x in range(base_icon.width()):
                for y in range(base_icon.height()):
                    if gray_image.pixelColor(x, y).alpha() != 0:
                        self.icons[color].setPixelColor(x, y, QtGui.QColor(color))
            # Save the image to a cache file for faster loading
            self.icons[color].save("cache/tell_tails/" + self.ros_name + "_" + color + ".png", "PNG", 100)

    def scale_icons(self, size):
        for key in self.icons:
            self.icons[key] = self.icons[key].scaled(size[0], size[1], QtCore.Qt.KeepAspectRatio,
                                                     QtCore.Qt.SmoothTransformation)
            self.icon_offset_x = (size[0] - self.icons[key].width()) // 2
            self.icon_offset_y = (size[1] - self.icons[key].height()) // 2

    def update(self) -> None:
        if self.blink:
            self.updated = True
            if self.selected_color == "gray":
                self.selected_color = self.display_color
            else:
                self.selected_color = "gray"
        else:
            self.selected_color = self.display_color

    # Set the tooltip to the hover text
    def enterEvent(self, event):
        self.setToolTip(f"{self.hover_text}: No data")
        super().enterEvent(event)

    def set_color(self, color):
        self.selected_color = color
        self.updated = True


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

        self.icon_size = (round(66 * 1), round(41 * 1))

        self.icon_rows = 4
        self.icon_cols = 6
        self.icon_surface_size = (self.icon_size[0] * self.icon_cols +
                                  AnnunciatorIcon.icon_gap_h * self.icon_cols,
                                  self.icon_size[1] * self.icon_rows +
                                  AnnunciatorIcon.icon_gap_v * self.icon_rows)
        self.icon_surface = QWidget(parent=self)
        # Set a boarder around the icon surface
        self.icon_surface.setStyleSheet("border: 1px solid black;")
        self.icon_surface.setFixedSize(*self.icon_surface_size)
        self.icon_surface.move(0, 0)
        self.icon_surface.paintEvent = self.paintEvent

        # Check if the icon cache directory exists and create it if it doesn't
        if not os.path.exists("cache/tell_tails"):
            os.makedirs("cache/tell_tails")

        self.load_icons()

        # Setup the timer to update the annunciator icons
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

    def load_icons(self):
        # Icons are stored in the resources' folder under annunciator_icons
        self.icon_mappings = json.load(open("resources/annunciator_icons/icon_mappings.json"))
        for file_name, info in self.icon_mappings.items():
            # Build an icon object for each icon
            self.icons[info["ros_name"]] = \
                AnnunciatorIcon("resources/annunciator_icons/" + file_name, info, size=self.icon_size,
                                parent=self.icon_surface)

    def update(self) -> None:
        # Update the annunciator icons
        for icon in self.icons.values():
            icon.update()
        should_redraw = False
        for icon in self.icons.values():
            if icon.updated:
                should_redraw = True
                icon.updated = False
        if should_redraw:
            super().update()

    def paintEvent(self, event):
        # Use the QtQuick paint engine to draw the icons
        painter = QtGui.QPainter(self.icon_surface)
        for icon in self.icons.values():
            # Draw each icon in the correct location
            try:
                if icon.built:
                    painter.drawImage(icon.x() + icon.icon_offset_x, icon.y() + icon.icon_offset_y,
                                      icon.icons[icon.selected_color])
            except Exception as e:
                logging.error(f"Error drawing annunciator icons: {e}")

    # When the main window is opened the annunciator will begin rezising the icons to fit the window
    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        for icon in self.icons.values():
            if not icon.built:
                icon.build_thread.start()
        super().showEvent(a0)
