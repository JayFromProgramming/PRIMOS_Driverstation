from PyQt5.QtWidgets import QWidget, QLabel


class ODriveMotor(QWidget):

    def __init__(self, screen_name, ros_name, parent=None):
        super().__init__()
        super().setParent(parent)
        super().setFixedSize(350, 50)
        self.screen_name = screen_name
        self.ros_name = ros_name

        self.parent = parent

        # -----------------        Name       -----------------
        # |  Speed   | Current | Mtr Temp | FET Temp | STATUS |
        # | 00.0 RPM |  00.0 A |  00.0 C  |  00.0 C  |  IDLE  |
        # -----------------------------------------------------

        self.surface = QWidget(self)

        # Apply a boarder to just the outer edge of the widget not the elements inside
        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        value_spacing = 10

        self.surface.setFixedSize(350, 50)
        self.surface.move(0, 0)

        self.speed_limits = (75, 100)       # (warn, max)
        self.current_limits = (10, 20)      # (warn, max)
        self.motor_temp_limits = (50, 100)  # (warn, max)
        self.fet_temp_limits = (50, 100)    # (warn, max)

        self.name_label = QLabel(screen_name, self.surface)
        self.name_label.move(round(self.surface.width() / 2 - self.name_label.width() / 2), 0)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px; text-align: center;"
                                      "background-color: transparent;")

        self.header = QLabel("     Speed    | Power | MTR Tmp | FET Tmp | State", self.surface)
        self.header.move(0, 17)
        self.header.setStyleSheet("font-weight: bold; font-size: 13px; border: 0px; background-color: transparent;")

        self.speed_label = QLabel(r"<pre>000.0RPM<\pre>", self.surface)
        self.speed_label.move(10, 33)
        self.speed_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                       " background-color: transparent;")

        self.current_label = QLabel(r"<pre>000.0A<\pre>", self.surface)
        self.current_label.move(self.speed_label.x() + 66 + value_spacing, 33)
        self.current_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                         " background-color: transparent;")

        self.motor_temp_label = QLabel(r"<pre>00.0C<\pre>", self.surface)
        self.motor_temp_label.move(self.current_label.x() + 57 + value_spacing, 33)
        self.motor_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                            " background-color: transparent;")

        self.fet_temp_label = QLabel(r"<pre>00.0C<\pre>", self.surface)
        self.fet_temp_label.move(self.motor_temp_label.x() + 55 + value_spacing, 33)
        self.fet_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                          " background-color: transparent;")

        self.status_label = QLabel(r"<pre>IDLE  <\pre>", self.surface)
        self.status_label.move(self.fet_temp_label.x() + 50 + value_spacing, 33)
        self.status_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                        " background-color: transparent;")

    def set_limits(self, speed: tuple, current: tuple, motor_temp: tuple, fet_temp: tuple):
        self.speed_limits = speed
        self.current_limits = current
        self.motor_temp_limits = motor_temp
        self.fet_temp_limits = fet_temp

    def update(self, speed=0, current=0, motor_temp=0, fet_temp=0, status="IDLE"):
        if speed > 100 or speed < -100:
            self.speed_label.setText(r"<pre>{:5.0f}RPM<\pre>".format(speed))
        else:
            self.speed_label.setText(r"<pre>{:5.1f}RPM<\pre>".format(speed))
        self.current_label.setText(r"<pre>{:5.1f}A<\pre>".format(current))
        self.motor_temp_label.setText(r"<pre>{:4.1f}C<\pre>".format(motor_temp))
        self.fet_temp_label.setText(r"<pre>{:4.1f}C<\pre>".format(fet_temp))
        self.status_label.setText(r"<pre>{:5s}<\pre>".format(status))

        if abs(speed) > self.speed_limits[1]:
            self.speed_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                           " background-color: transparent; color: orange;")
        elif abs(speed) > self.speed_limits[0]:
            self.speed_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                           " background-color: transparent; color: red;")
        else:
            self.speed_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                           " background-color: transparent; color: DarkGreen;")

        if abs(current) > self.current_limits[1]:
            self.current_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                             " background-color: transparent; color: orange;")
        elif abs(current) > self.current_limits[0]:
            self.current_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                             " background-color: transparent; color: red;")
        else:
            self.current_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                             " background-color: transparent; color: DarkGreen;")

        if motor_temp > self.motor_temp_limits[1]:
            self.motor_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                                " background-color: transparent; color: orange;")
        elif motor_temp > self.motor_temp_limits[0]:
            self.motor_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                                " background-color: transparent; color: red;")
        else:
            self.motor_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                                " background-color: transparent; color: DarkGreen;")

        if fet_temp > self.fet_temp_limits[1]:
            self.fet_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                              " background-color: transparent; color: orange;")
        elif fet_temp > self.fet_temp_limits[0]:
            self.fet_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                              " background-color: transparent; color: red;")
        else:
            self.fet_temp_label.setStyleSheet("font-size: 13px; font-weight: bold; border: 0px;"
                                              " background-color: transparent; color: DarkGreen;")


