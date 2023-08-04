quarter_modules = ["Front_Left", "Front_Right", "Rear_Left", "Rear_Right"]


class ODriveCommands:
    E_STOP = 0
    IDLE = 1
    CLEAR_ERRORS = 2
    SET_CLOSED_LOOP = 3
    SET_POINT = 4
    BEGIN_CALIBRATION = 5
    SET_VEL_LIMIT = 6


class ODriveInputModes:
    MOTOR_INACTIVE = 0x0
    PASSTHROUGH = 0x1
    VEL_RAMP = 0x2
    POS_FILTER = 0x3
    MIX_CHANNELS = 0x4
    TRAP_TRAJ = 0x5
    TORQUE_RAMP = 0x6
    MIRROR = 0x7
    TUNING = 0x8
    UNKNOWN_INPUT_MODE = 0xFF


class ActuatorCommands:
    STOP = 0
    SET_DUTY_CYCLE = 1
    SET_POSITION = 2


class EStopCommands:
    TRIGGER = 0
    RESET = 1
    ENABLE_AUTO = 2
    DISABLE_AUTO = 3


class SuspensionModes:
    DEFAULT = 0
    INITIAL_RAMP = 1
    EXTRA_RAMP_1 = 2
    EXTRA_RAMP_2 = 3
    MANUAL = 4


class SteeringStates:
    PARKED = 0
    DRIVING = 1
    TURNING = 2
