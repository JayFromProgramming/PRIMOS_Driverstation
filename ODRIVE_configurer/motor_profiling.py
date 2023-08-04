import datetime
import os
import time

import odrive
import csv
from odrive.enums import *
from odrive.utils import dump_errors


class profiler:

    def __init__(self):
        self.motor = odrive.find_any(timeout=10)
        self.axis = self.motor.axis0

        self.rpm_interval = 100
        self.rpm_max = 2000
        self.test_length = 15  # seconds
        self.sample_rate = 60  # Hz
        self.test_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if not os.path.exists(f"motor_profile_{self.test_time}"):
            os.mkdir(f"motor_profile_{self.test_time}")
        self.axis.config.enable_watchdog = True
        self.motor.clear_errors()

    def run_test(self, test_rpm):
        print(f"Running test at {test_rpm} rpm")
        dump_errors(self.motor)
        self.motor.clear_errors()
        self.axis.controller.config.control_mode = ControlMode.VELOCITY_CONTROL
        self.axis.controller.config.input_mode = InputMode.VEL_RAMP
        self.axis.controller.input_vel = test_rpm / 60
        self.axis.requested_state = AxisState.CLOSED_LOOP_CONTROL

        with open(f"motor_profile_{self.test_time}/{test_rpm}rpm.csv", "w") as f:
            writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
            writer.writerow(["elapsed", "rpm", "torque", "power", "bus_voltage", "bus_current"])
            start_time = time.time()
            while time.time() - start_time < self.test_length and \
                    self.axis.current_state == AxisState.CLOSED_LOOP_CONTROL:
                self.axis.controller.input_vel = test_rpm / 60
                writer.writerow([time.time() - start_time, self.axis.pos_vel_mapper.vel * 60,
                                 self.axis.motor.torque_estimate, self.axis.motor.electrical_power,
                                 self.motor.vbus_voltage, self.motor.ibus])
                time.sleep(1 / self.sample_rate)
                self.axis.watchdog_feed()

            if self.axis.current_state != AxisState.CLOSED_LOOP_CONTROL:
                print(f"Test failed at {test_rpm} rpm")
                self.axis.controller.input_vel = 0
                self.axis.requested_state = AxisState.IDLE
                writer.writerow(["Test failed", self.axis.current_state, self.axis.error])
                time.sleep(2)
                return

        self.axis.controller.input_vel = 0
        self.axis.requested_state = AxisState.IDLE
        time.sleep(2)

    def run_profile(self):
        for rpm in range(100, self.rpm_max, self.rpm_interval):
            self.run_test(rpm)


if __name__ == "__main__":
    print("Starting motor profiling...")
    profiler = profiler()
    profiler.run_profile()
