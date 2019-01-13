
from wpilib import AnalogInput


class InfraredSensor(AnalogInput):

    def __init__(self, channel):
        super().__init__(channel)

    def GetVoltage(self):
        return super().getVoltage()

    def GetMedianVoltage(self):
        return super().getVoltage()
