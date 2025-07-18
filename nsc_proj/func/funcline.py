import cv2
import robomaster
from robomaster import robot
from robomaster import vision
import time

class PointInfo:
    def __init__(self, x, y, ceta, c):
        self._x = x
        self._y = y
        self._ceta = ceta
        self._c = c

    @property
    def pt(self):
        return int(self._x * 1280), int(self._y * 720)

    @property
    def color(self):
        return 255, 255, 255
    
# PID con. for line
def line_pid_control(error, prev_error, integral, l_kp, l_ki, l_kd):
    derivative = error - prev_error
    integral += error
    control = l_kp * error + l_ki * integral + l_kd * derivative
    return control, integral

def on_detect_line(line_info):
    global line_type_detected, line
    number = len(line_info)
    line.clear()

    if number > 0:
        
        for i in range(1, number):
            x, y, ceta, c = line_info[i]
            line.append(PointInfo(x, y, ceta, c))
            line_type = line_info[0]
            if line_type == 2:
                line_type_detected = True

if __name__ == '__main__':
    robomaster.config.Local_IP_STR = "192.168.2.36"
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')

 # variables for line
    line = []
    line_type_detected = False

    # PID control for line
    l_kp = 0.5
    l_ki = 0.01
    l_kd = 0.1
    integral = 0.0
    prev_error = 0.0

    ep_chassis = ep_robot.chassis
    ep_arm = ep_robot.robotic_arm
    ep_sensor = ep_robot.sensor
    ep_gripper = ep_robot.gripper
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera

# loop for line
    ep_vision.sub_detect_info(name="line", color="red", callback=on_detect_line)
    img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
    
    while not line_type_detected:
        for pt in line:
            cv2.circle(img, pt.pt, 3, pt.color, -1) 

            if line:
                center_x = line[0]._x * 1280
                error = 640 - center_x 

                control, integral = line_pid_control(error, prev_error, integral, l_kp, l_ki, l_kd)
                prev_error = error

                ep_chassis.drive_speed(x=0.3, y=0, z=-control, timeout = 3)

            else:
                ep_robot.play_sound(robot.SOUND_ID_1A).wait_for_completed()
                ep_chassis.drive_speed(x=0, y=0, z=0)


        cv2.imshow("Line", img)
        cv2.waitKey(1)
        
        if line_type_detected == True: # line_type = 2
            ep_vision.unsub_detect_info(name="line")
            ep_chassis.drive_speed(x=0, y=0, z=0, timeout = 3)
            cv2.destroyAllWindows()
            time.sleep(3)
            ep_robot.play_sound(robot.SOUND_ID_1B).wait_for_completed()
            break