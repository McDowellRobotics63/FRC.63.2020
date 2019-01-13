
from wpilib.command import CommandGroup
from commands_lift.auto_set_lift_position import AutoSetLiftPosition
from commands_drive.auto_drive_fixed_distance import AutoDriveFixedDistance
from commands_drive.auto_rotate import AutoRotate

class DownAndBack(CommandGroup):
    def __init__(self, robot):
        super().__init__()

        self.addParallel(AutoSetLiftPosition(robot, 30))
        self.addSequential(AutoDriveFixedDistance(robot, 300))
        self.addSequential(AutoRotate(robot, 100))
        self.addParallel(AutoSetLiftPosition(robot, 1))
        self.addSequential(AutoDriveFixedDistance(robot, 150))
