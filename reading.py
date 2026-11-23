
import math
from rtde_receive import RTDEReceiveInterface

def get_position(IP):

    robot_read = RTDEReceiveInterface(IP)

    position = robot_read.getActualTCPPose()

    print("X0=", position[0])
    print("Y0=", position[1])
    print("Z0=", position[2])

    print("RX=", position[3])#Transform them from radians to degrees
    print("RY=", position[4])
    print("RZ=", position[5])

    robot_read.disconnect()
    
    return position

def get_speed(IP):
    receive = RTDEReceiveInterface(IP)

    try:
        return receive.getActualTCPSpeed()
    finally:
        receive.disconnect()