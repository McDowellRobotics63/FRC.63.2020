#Why have you forsaken me, father?
class BallRakeState(Enum):
    DEPLOY_BEGIN = 0
    RAKE_DEPLOY_WAIT = 1
    RAKE_MOTOR_START = 2
    STOW_BEGIN = 3
    RAKE_STOW = 4
    RAKE_STOW_WAIT = 5
    RAKE_STOWED = 6

    HATCH_OPEN = 7
    HATCH_OPEN_WAIT = 8
    BALL_MOTORS_START = 9
    HATCH_CLOSED = 12

