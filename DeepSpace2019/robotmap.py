
import math

PIGEON_UNITS_PER_ROTATION = 8192
DRIVE_ENCODER_COUNTS_PER_REV = 1440
WHEEL_DIAMETER = 3  # 6 inches
WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER
BASE_TRAJECTORY_PERIOD_MS = 20

MIN_POSITION_LIFT = 0 #ticks
MAX_POSITION_LIFT = 25 #ticks
MIN_POSITION_WRIST = 0 #ticks
MAX_POSITION_WRIST = 30 #ticks


#Talon CAN IDs
DRIVE_LEFT_MASTER_CAN_ID = 3
DRIVE_LEFT_SLAVE_CAN_ID = 4
DRIVE_RIGHT_MASTER_CAN_ID = 2
DRIVE_RIGHT_SLAVE_CAN_ID = 1
CLAW_LEFT_WHEELS_CAN_ID = 5
CLAW_RIGHT_WHEELS_CAN_ID = 6
CLAW_WRIST_CAN_ID = 8
LIFT_CAN_ID = 7
PIGEON_IMU_CAN_ID = 12

CAN_TIMEOUT_MS = 10

#Solenoid Mappings
PCM1_CANID = 9
PCM2_CANID = 10
DRIVE_FRONT_EXTEND_SOLENOID = 3
DRIVE_FRONT_RETRACT_SOLENOID = 2
DRIVE_REAR_EXTEND_SOLENOID = 4
DRIVE_REAR_RETRACT_SOLENOID = 5
CLAW_OPEN_SOLENOID = 2
CLAW_CLOSE_SOLENOID = 3
HARPOON_OUTSIDE_EXTEND_SOLENOID = 1
HARPOON_OUTSIDE_RETRACT_SOLENOID = 0
HARPOON_CENTER_EXTEND_SOLENOID = 5
HARPOON_CENTER_RETRACT_SOLENOID = 4
LIFT_RAISE_SOLENOID = 0
LIFT_LOWER_SOLENOID = 1

#Digital Inputs
AUTO_SWITCH_1 = 0
AUTO_SWITCH_2 = 1
AUTO_SWITCH_3 = 2
BALL_IR_SENSOR = 3

#Controller Map
XBOX_LEFT_X_AXIS = 0
XBOX_LEFT_Y_AXIS = 1
XBOX_LEFT_TRIGGER_AXIS = 2
XBOX_RIGHT_TRIGGER_AXIS = 3
XBOX_RIGHT_X_AXIS = 4
XBOX_RIGHT_Y_AXIS = 5
XBOX_A = 1
XBOX_B = 2
XBOX_X = 3
XBOX_Y = 4
XBOX_LEFT_BUMPER = 5
XBOX_RIGHT_BUMPER = 6
XBOX_BACK = 7
XBOX_START = 8