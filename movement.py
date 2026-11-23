import os
import sys
import time
import math
import reading
from rtde_receive import RTDEReceiveInterface

velocity = 0.25
aceleration = 0.05
TOLERANCE = 0.001   # 1 mm
TIMEOUT = 30        # seconds


def move(robot_control, position, asynchronous):
    if not robot_control.isPoseWithinSafetyLimits(position):
        print("Position outside configured safety limits.")
        return False
    return robot_control.moveL(position, velocity, aceleration, asynchronous)


def stop(robot_control, ROBOT_IP):
    print("Stopping robot...")
    robot_control.stopL(0.75)

    print("WARNING: Could not confirm that the robot stopped.")
    return False


# --- Non-blocking key reading ---
if os.name == "nt":
    import msvcrt

    def _key_pressed():
        if msvcrt.kbhit():
            return msvcrt.getwch().lower()
        return None
else:
    import select
    import termios
    import tty

    def _key_pressed():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1).lower()
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _wait_or_stop(robot_control, ROBOT_IP, rtde_r, target):
    # Returns True if the target was reached, False if stopped or timed out
    start = time.time()
    while True:
        if _key_pressed() == "s":
            stop(robot_control, ROBOT_IP)
            return False

        tcp = rtde_r.getActualTCPPose()
        if math.dist(tcp[:3], target[:3]) < TOLERANCE:
            robot_control.stopL(0.75)   # ends the async movement cleanly
            return True

        if time.time() - start > TIMEOUT:
            print("Timeout waiting for the robot.")
            stop(robot_control, ROBOT_IP)
            return False

        time.sleep(0.05)


def move_home(robot_control, ROBOT_IP, Home_position, lift=0.03):
    above = list(Home_position)
    above[2] += lift

    rtde_r = RTDEReceiveInterface(ROBOT_IP)
    try:
        for target in (above, list(Home_position)):
            if not move(robot_control, target, True):
                return False
            if not _wait_or_stop(robot_control, ROBOT_IP, rtde_r, target):
                print("Movement to HOME cancelled.")
                return False
        print("Robot at HOME.")
        return True
    finally:
        rtde_r.disconnect()