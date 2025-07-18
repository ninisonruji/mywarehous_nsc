import cv2
import time
import robomaster
from robomaster import robot
from robomaster import vision

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

class LineDetector:
    def __init__(self):
        self.line_type_detected = False
        self.line_points = []

    def on_detect_line(self, line_info):
        number = len(line_info)
        self.line_points.clear()

        if number > 0:
            for i in range(1, number):
                x, y, ceta, c = line_info[i]
                self.line_points.append(PointInfo(x, y, ceta, c))

            line_type = line_info[0]
            if line_type == 2:
                self.line_type_detected = True
    
# ========================
# PID Controller Function
# ========================

def pid_control(error, prev_error, integral, kp, ki, kd):
    derivative = error - prev_error
    integral += error
    control = (kp * error) + (ki * integral) + (kd * derivative)
    return control, integral

product_marker_map = {
    "A1": 101,
    "A2": 102,
    "A3": 103,
    "B1": 201,
    "B2": 202,
    "B3": 203
}

# ========================
# Main Function
# ========================

def run_line_following():
    robomaster.config.LOCAL_IP_STR = "192.168.2.36"
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')

    ep_chassis = ep_robot.chassis
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera

    detector = LineDetector()
    ep_vision.sub_detect_info(name="line", color="red", callback=detector.on_detect_line)

    # PID config
    kp, ki, kd = 0.5, 0.01, 0.1
    integral = 0.0
    prev_error = 0.0

    while not detector.line_type_detected:
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)

        if detector.line_points:
            pt = detector.line_points[0]
            cv2.circle(img, pt.pt, 3, pt.color, -1)

            center_x = pt.x * 1280
            error = 640 - center_x

            control, integral = pid_control(error, prev_error, integral, kp, ki, kd)
            prev_error = error

            ep_chassis.drive_speed(x=0.3, y=0, z=-control, timeout=0.5)
        else:
            ep_chassis.drive_speed(x=0, y=0, z=0)

        cv2.imshow("Line", img)
        cv2.waitKey(1)

    # พบทางแยก line type 2
    ep_vision.unsub_detect_info(name="line")
    ep_chassis.drive_speed(x=0, y=0, z=0)
    cv2.destroyAllWindows()
    time.sleep(1)
    ep_robot.play_sound(robot.SOUND_ID_1B).wait_for_completed()

    ep_robot.close()
