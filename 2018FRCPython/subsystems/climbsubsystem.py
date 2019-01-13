import robotmap

from wpilib.command.subsystem import Subsystem
from wpilib import Solenoid
from wpilib import DigitalInput
from wpilib import Spark

class ClimbSubsystem(Subsystem):

    def __init__(self, robot):
        super().__init__("Climb")
        self.robot = robot

        self.winchMotor = Spark(robotmap.CLIMBWINCH)
        self.armUpSolenoid = Solenoid(robotmap.CLIMBARM_UP)
        self.armDownSolenoid = Solenoid(robotmap.CLIMBARM_DOWN)
        self.lockCloseSolenoid = Solenoid(robotmap.CLIMBCLAMPLOCK_CLOSE)
        self.lockOpenSolenoid = Solenoid(robotmap.CLIMBCLAMPLOCK_OPEN)
        self.hookLimit = DigitalInput(robotmap.LIMIT_SWITCH_HOOK)

    def pullyclimb(self, speed):
        self.winchMotor.set(speed)

    def armExtend(self):
        self.armUpSolenoid.set(True)
        self.armDownSolenoid.set(False)

    def armRetract(self):
        self.armUpSolenoid.set(False)
        self.armDownSolenoid.set(True)

    def clampLock(self):
        self.lockCloseSolenoid.set(True)
        self.lockOpenSolenoid.set(False)

    def clampOpen(self):
        self.lockCloseSolenoid.set(False)
        self.lockOpenSolenoid.set(True)

    def isHookPressed(self):
        return self.hookLimit.get() == False
