from rtde_control import RTDEControlInterface

#Importing User-defined modules
import reading
import movement
import paint

ROBOT_IP = "192.168.1.100"
PORT = 30002
robot_control = RTDEControlInterface(ROBOT_IP)

#Centre position of the paper=============================
#X0= -0.35390039958047365
#Y0= 0.09824047482014538
#Z0= 0.06855666196307708

#Home wall
X0= -0.3773991937003181
Y0= 0.07711132442464358
Z0= 0.495401552797184
RX= 0.09363323156443809
RY= -1.5699169510617974
RZ= -0.09953505239536767

#Joints angles-->the same in the whole program
#RX= -0.26287110754823945
#RY= 3.1054914621833305
#RZ= 0.022027003911903167

#A4 paper measure: 0.297m x 0.210m
#Top-left corner position of the paper=============================
#X0 = X0 - 0.296999990940094/2
#Y0 = Y0 - 0.20999999344348907/2


Home_position = [X0,Y0,Z0,RX,RY,RZ]

#==========================================


#Menu options=================================
try:
    while True:
        print("\nUR3 Robot Control")
        print("================================")
        print("- [p] Show current position.")
        print("- [h] Move to HOME(centre of the paper) position.")
        print("- [s] Stop.")
        print("- [j] Painting json file.")
        print("- [x] Exit.\n")

        opcion = input("Select an option: ").strip().lower()

        match opcion:
            case "p":

                reading.get_position(ROBOT_IP)
            
            case "h":
                print("Robot moving... Press 's' to stop.")
                movement.move_home(robot_control,ROBOT_IP,Home_position,lift=0.03)
            
            case "s":
                
                robot_speed = reading.get_speed(ROBOT_IP)
                #Test if the velocity is already 0---> robot stopped
                if any(abs(v) > 0.001 for v in robot_speed):
                    movement.stop(robot_control)
                else:
                    print("Robot is already stopped.")
            
            case "j":

                #paint.figure(robot_control,Home_position)
                paint.JSON(robot_control,ROBOT_IP,Home_position)
                print("Starting painting json file...")
            
            case "x":

                #For securities reasons, is safer to test if the robot is stopped before existing from the program
                robot_speed = reading.get_speed(ROBOT_IP)
                if any(abs(v) > 0.001 for v in robot_speed):
                    print("Can't exit from the program cause the robot is still moving. Please stop it first")
                else:
                    print("Exited from the program")
                    break
            
            case _:
                print("Invalid option. Please try again.")
finally:
    robot_control.stopScript()
    robot_control.disconnect()
#==================================================



