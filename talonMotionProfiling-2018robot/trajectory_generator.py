
import pathfinder as pf
import pickle

# Pathfinder constants
MAX_VELOCITY = 2  # ft/s
MAX_ACCELERATION = 2 #ft/s/s
PERIOD = 0.02
MAX_JERK = 120.0

# Set up the trajectory
points = [pf.Waypoint(0, 0, 0), pf.Waypoint(9, 6, 0)]

info, trajectory = pf.generate(
    points,
    pf.FIT_HERMITE_CUBIC,
    pf.SAMPLES_HIGH,
    dt=PERIOD,
    max_velocity=MAX_VELOCITY,
    max_acceleration=MAX_ACCELERATION,
    max_jerk=MAX_JERK,
)

with open("/home/ubuntu/traj", "wb") as fp:
    pickle.dump(trajectory, fp)
