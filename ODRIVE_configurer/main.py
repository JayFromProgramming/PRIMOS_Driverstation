import json
import math
import msvcrt
import time

import odrive
from odrive.enums import EncoderId, GpioMode, AxisState, ControlMode, InputMode, ProcedureResult, ODriveError
from odrive.utils import dump_errors


def main(node_id, setup_can=True, calibrate=True):
    print(f"Connecting to ODrive...")

    try:
        odrv0 = odrive.find_any(timeout=10)
    except Exception as e:
        print(f"Unable to connect to ODrive ({type(e).__name__}): {e}")
        return

    # print(odrv0.__dict__)
    # dicts = odrv0.__dict__
    # for key in dicts:
    #     print(key)
    #     print(dicts[key])
    print(f"Connected to ODrive {odrv0.serial_number}")

    # Clear errors
    odrv0.clear_errors()

    # Setup can bus
    if setup_can:
        print(f"Setting up CAN bus...")
        # odrv0.erase_configuration()
        odrv0.config.enable_can_a = True
        odrv0.axis0.config.can.node_id = node_id
    odrv0.can.config.baud_rate = 500000
    odrv0.axis0.config.can.encoder_msg_rate_ms = 25
    odrv0.axis0.config.can.temperature_msg_rate_ms = 100
    odrv0.axis0.config.can.bus_voltage_msg_rate_ms = 100
    odrv0.axis0.config.can.iq_msg_rate_ms = 100
    odrv0.axis0.config.can.heartbeat_msg_rate_ms = 100
    odrv0.axis0.config.can.error_msg_rate_ms = 100
    odrv0.axis0.config.can.torques_msg_rate_ms = 100
    # odrv0.axis0.config.can.

    # Get the config values from motor_configs.json
    with open("motor_configs.json", "r") as f:
        motor_configs = json.load(f)

    odrv0.clear_errors()

    motor_configs = motor_configs[str(odrv0.axis0.config.can.node_id)]

    # Setup motor
    print(f"Setting up motor...")
    odrv0.axis0.config.motor.motor_type = 0  # 0 HIGH_CURRENT, 1 GIMBAL
    odrv0.axis0.config.motor.pole_pairs = motor_configs["pole_pairs"]
    odrv0.axis0.config.motor.calibration_current = motor_configs["calibration_current"]
    odrv0.axis0.config.calibration_lockin.current = motor_configs["calibration_lockin_current"]
    odrv0.axis0.config.motor.torque_constant = motor_configs["torque_constant"]

    # Setup more motor
    odrv0.axis0.config.motor.current_soft_max = motor_configs["current_soft_max"]
    odrv0.axis0.config.motor.current_hard_max = motor_configs["current_hard_max"]

    odrv0.axis0.config.torque_soft_min = motor_configs["torque_soft_min"]
    odrv0.axis0.config.torque_soft_max = motor_configs["torque_soft_max"]
    # odrv0.axis0.config.torque_hard_max = 2.43373  # Nm

    odrv0.axis0.controller.config.vel_limit = motor_configs["vel_limit"]
    odrv0.axis0.controller.config.vel_limit_tolerance = motor_configs["vel_limit_tolerance"]

    odrv0.axis0.controller.config.spinout_electrical_power_threshold = motor_configs["spinout_electrical_power_threshold"]
    odrv0.axis0.controller.config.spinout_mechanical_power_threshold = motor_configs["spinout_mechanical_power_threshold"]

    # odrv0.axis0.config.motor.resistance_calib_max_voltage = motor_configs["calibration_voltage"]

    if "thermistor_enable" in motor_configs:
        odrv0.axis0.motor.motor_thermistor.config.r_ref = motor_configs["thermistor_r_ref"]
        odrv0.axis0.motor.motor_thermistor.config.beta = motor_configs["thermistor_beta"]
        odrv0.axis0.motor.motor_thermistor.config.enabled = False
    else:
        odrv0.axis0.config.motor_thermistor.config.enabled = False

    if "reversed" in motor_configs:
        odrv0.axis0.config.motor.direction = -1 if motor_configs["reversed"] else 1

    odrv0.axis0.controller.config.enable_vel_limit = True
    odrv0.axis0.controller.config.enable_overspeed_error = False
    odrv0.axis0.controller.config.enable_torque_mode_vel_limit = True

    # odrv0.axis0.

    odrv0.config.dc_bus_overvoltage_trip_level = 55
    odrv0.config.dc_bus_undervoltage_trip_level = 45

    odrv0.config.dc_max_negative_current = motor_configs["dc_max_negative_current"]

    # odrv0.axis0.controller.config.vel_integrator_gain = 0.32
    # odrv0.axis0.controller.config.vel_integrator_limit = 50

    odrv0.axis0.config.enable_watchdog = False
    odrv0.axis0.config.watchdog_timeout = 1

    # Clear errors
    odrv0.clear_errors()

    # Save config
    try:
        print(f"Saving configuration...")
        odrv0.save_configuration()
    except Exception as e:
        print(f"Unable to save configuration ({type(e).__name__}): {e}")

    odrv0 = odrive.find_any(timeout=10)

    # Validate config
    print(f"Validating configuration...")
    if odrv0.axis0.config.can.node_id == node_id:
        print(f"Node ID set to {node_id}")
    else:
        print(f"Node ID not set to {node_id} instead {odrv0.axis0.config.can.node_id}")

    odrv0.axis0.config.encoder_bandwidth = 100
    odrv0.hall_encoder0.config.enabled = True
    odrv0.axis0.config.load_encoder = EncoderId.HALL_ENCODER0
    odrv0.axis0.config.commutation_encoder = EncoderId.HALL_ENCODER0

    odrv0.axis0.controller.config.vel_ramp_rate = 20

    # odrv0.save_configuration()

    try:
        odrv0.save_configuration()
    except Exception as e:
        print(f"Unable to save configuration ({type(e).__name__}): {e}")

    odrv0 = odrive.find_any(timeout=10)

    odrv0.clear_errors()

    if calibrate:

        print("Motor setup complete, beginning motor calibration...")
        while odrv0.axis0.active_errors == ODriveError.INITIALIZING:
            print(f"Waiting for motor to initialize...")
            time.sleep(1)
        odrv0.axis0.requested_state = AxisState.MOTOR_CALIBRATION
        time.sleep(1)
        while odrv0.axis0.current_state == AxisState.MOTOR_CALIBRATION:
            print(f"Waiting for motor calibration to complete...")
            time.sleep(0.1)
        dump_errors(odrv0)
        time.sleep(2)

        while odrv0.axis0.active_errors == ODriveError.INITIALIZING:
            print(f"Waiting for motor to initialize...")
            time.sleep(1)

        print("Beginning calibration Hall Polarity Calibration")
        odrv0.axis0.requested_state = AxisState.ENCODER_HALL_POLARITY_CALIBRATION
        time.sleep(1)
        while odrv0.axis0.current_state == AxisState.ENCODER_HALL_POLARITY_CALIBRATION:
            time.sleep(0.1)
            odrv0.axis0.watchdog_feed()
        dump_errors(odrv0)
        print("Beginning calibration Hall Phase Calibration")
        odrv0.axis0.requested_state = AxisState.ENCODER_HALL_PHASE_CALIBRATION
        time.sleep(1)
        while odrv0.axis0.current_state == AxisState.ENCODER_HALL_PHASE_CALIBRATION:
            time.sleep(0.1)
            odrv0.axis0.watchdog_feed()
        dump_errors(odrv0)
        time.sleep(2)

        odrv0.axis0.config.enable_watchdog = True
        odrv0.axis0.config.watchdog_timeout = 1
        try:
            print("Saving configuration...")
            odrv0.save_configuration()
        except Exception as e:
            print(f"Unable to save configuration ({type(e).__name__}): {e}")


if __name__ == "__main__":
    # Get the node ID of the motor
    odrive = odrive.find_any(timeout=10)
    node_id = odrive.axis0.config.can.node_id
    # Ask the user if this is the correct node ID
    print(f"Found motor with node ID {node_id}")
    if input("Is this the correct node ID? (y/n): ").lower() == "n":
        node_id = int(input("Enter the new node ID: "))
    # Run the main function
    print("Would you like to calibrate the motor? (y/n): ")
    calibrate = input().lower() == "y"
    main(node_id, setup_can=True, calibrate=calibrate)
