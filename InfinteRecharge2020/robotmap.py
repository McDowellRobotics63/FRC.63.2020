import math

#Wheel Stuff
WHEEL_DIAMETER = 0.5 #ft
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * math.pi #ft/rev
ENCODER_UNITS_PER_REV = 3600 #units/rev 1250 maybe
FEET_PER_UNIT = WHEEL_CIRCUMFERENCE / ENCODER_UNITS_PER_REV #ft/unit

CAN_TIMEOUT_MS = 25

#Talon CAN IDs
FRONT_LEFT_ID = 4
REAR_LEFT_ID = 2
REAR_RIGHT_ID = 1
FRONT_RIGHT_ID = 3

LIFT_WINCH_ID = 0

COMPRESSOR_CAN_ID = 0

#Spark Controllers
BOTTOM_INTAKE_ID = 6
BALL_TICKLER_ID = 7 #Top Intake
RAKE_ID = 9

COLOR_WHEEL_ID = 8

#Solenoid IDs
    #PCM 1#
PCM_ID = 1

COLOR_WHEEL_EXTEND_SOLENOID = 0
COLOR_WHEEL_RETRACT_SOLENOID = 1

CLIMB_EXTEND_SOLENOID = 2
CLIMB_RETRACT_SOLENOID = 3

HOOK_EXTEND_SOLENOID = 4
HOOK_RETRACT_SOLENOID = 5

    #PCM 2#
PCM2_ID = 2

BALL_HATCH_EXTEND_SOLENOID = 0
BALL_HATCH_RETRACT_SOLENOID = 1

BALL_RAKE_EXTEND_SOLENOID = 2
BALL_RAKE_RETRACT_SOLENOID = 3

HOOK_RELEASE_EXTEND_SOLENOID = 4
HOOK_RELEASE_RETRACT_SOLENOID = 5


#Controller Mappings
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