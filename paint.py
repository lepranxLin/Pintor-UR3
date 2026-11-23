import json
import math
from pathlib import Path
import movement
import sys
import time

SPEED = 0.8       # m/s
ACC = 0.3         # m/s²
BLEND = 0.003     # radio de blend máximo (3 mm)
LIFT = 0.03       # separación de la pared al levantar el bolígrafo (cambia el signo si va hacia el otro lado)

def stop_requested():
    #Checks without blocking if the user pressed 's'
    if sys.platform.startswith("win"):
        import msvcrt
        while msvcrt.kbhit():
            if msvcrt.getwch().lower() == "s":
                return True
        return False
    else:
        import select
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.readline().strip().lower() == "s"
        return False

def JSON(robot_control,ROBOT_IP,Home_position):

    #Json file reading-----------------------------
    file_path = Path(__file__).with_name("cuadrado.json")

    with open(file_path, "r", encoding="utf-8") as f:
        drawing = json.load(f)

    lines = drawing["trazos"]

    movement.move(robot_control,Home_position,False)
    print("Robot moving... Press 's' to stop.")

    wall_x = Home_position[0]        #X where the pen touches the wall
    lifted_x = wall_x + LIFT         #X with the pen raised, away from the wall
    path = []  #All the points of the drawing, sent together to the robot

    #Pint the Json file------------------------------
    for line in lines:
        points = line["puntos"]

        #Go in front of the first point of the line with the pen raised
        y = Home_position[1] + points[0]["y"]
        z = Home_position[2] + points[0]["x"]
        path.append([lifted_x,y,z])

        for point in points:
            y = Home_position[1] + point["y"]
            z = Home_position[2] + point["x"]
            path.append([wall_x,y,z])#Now, the pen is touching the wall

        #Everytime that the robot finishes painting a line, move the pen away from the wall
        path.append([lifted_x,y,z])

    #Remove consecutive repeated points (distance 0 breaks the blend)
    clean = [path[0]]
    for p in path[1:]:
        if math.dist(p, clean[-1]) > 1e-4:
            clean.append(p)
    path = clean

    #Add orientation, speed, acceleration and blend to every point
    waypoints = []
    for i, p in enumerate(path):
        blend = 0.0
        #Blend only between points where the pen is touching the wall
        if 0 < i < len(path) - 1 and p[0] == wall_x \
           and path[i-1][0] == wall_x and path[i+1][0] == wall_x:
            blend = min(BLEND,
                        math.dist(p, path[i-1]) / 2.1,
                        math.dist(p, path[i+1]) / 2.1)
        waypoints.append(p + [Home_position[3],Home_position[4],Home_position[5],SPEED,ACC,blend])

    robot_control.moveL(waypoints,True)   #Asynchronous: the program keeps running while the robot moves

    #Wait until the drawing is finished, checking the 's' key all the time
    while robot_control.getAsyncOperationProgress() >= 0:
        if stop_requested():
            movement.stop(robot_control,ROBOT_IP)
            print("Drawing stopped.")
            return
        time.sleep(0.01)

    print("Drawing finished.")