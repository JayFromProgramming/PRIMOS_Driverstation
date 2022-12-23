import random
import time

from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QLabel
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


class BatteryUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.battery = self.robot.get_state("battery_state")

        self.surface = QWidget(self)
        self.surface.setFixedSize(638, 204)
        super().setFixedSize(638, 204)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: gray;")

        self.header = QLabel("Battery Info", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px;"
                                  " background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2), 0)

        self.graph = PlotWidget(self.surface)

        # The graph will use the right hand side of the surface
        self.graph.setLabel('left', 'Voltage', units='V')
        self.graph.setLabel('bottom', 'Time', units='s')
        self.graph.setYRange(36, 52)
        self.graph.setXRange(0, 60)
        self.graph.showGrid(x=True, y=True)
        self.graph.move(300, 30)
        self.graph.resize(300, 150)

        self.graph.setBackground('black')

        self.battery_voltage_samples = []
        self.battery_voltage_times = []

        self.battery_voltage_label = QLabel("Voltage:  XX.X V", self.surface)
        self.battery_voltage_label.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px;"
                                                 " background-color: transparent;")
        self.battery_voltage_label.move(10, 30)

        self.battery_current_label = QLabel("Current:  XX.X A", self.surface)
        self.battery_current_label.setStyleSheet("font-weight: bold; font-size: 17px; border: 0px;"
                                                    " background-color: transparent;")
        self.battery_current_label.move(10, 50)


        # Setup the update timer
        self.timer = Qt.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

        self.redraw_timer = Qt.QTimer()
        self.redraw_timer.timeout.connect(self.redraw_graph)
        self.redraw_timer.start(2000)

    def redraw_graph(self):
        # Clear the graph
        self.graph.clear()

        self.graph.plot(self.battery_voltage_times, self.battery_voltage_samples, pen=pg.mkPen('r', width=2))

    def update(self):

        # Get time since program start

        self.battery_voltage_times.append(time.process_time_ns() / 1000000000)  # Temporarily using time.time() until we get ROS time

        # Temporarily using random values until we get battery data
        self.battery_voltage_samples.append(random.randint(360, 520) / 10)

        # Trim the data to the last 60 seconds
        if len(self.battery_voltage_times) > 120:
            self.battery_voltage_times.pop(0)
            self.battery_voltage_samples.pop(0)

