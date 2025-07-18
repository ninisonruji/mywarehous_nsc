import cv2
import time
import robomaster
from robomaster import robot, vision

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

class MarkerInfo:
    def __init__(self, x, y, w, h, info):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._info = info
    @property
    def pt1(self):
        return int((self._x - self._w / 2) * 1280), int((self._y - self._h / 2) * 720)
    @property
    def pt2(self):
        return int((self._x + self._w / 2) * 1280), int((self._y + self._h / 2) * 720)
    @property
    def center(self):
        return int(self._x * 1280), int(self._y * 720)
    @property
    def text(self):
        return self._info

# === Global State ===
line = []
line_type_detected = False
markers = []

# === Callback ===
def on_detect_line(line_info):
    global line_type_detected, line
    line.clear()
    if len(line_info) > 0:
        for i in range(1, len(line_info)):
            x, y, ceta, c = line_info[i]
            line.append(PointInfo(x, y, ceta, c))
        if line_info[0] == 2:
            line_type_detected = True

def on_detect_marker(marker_info):
    markers.clear()
    for i in range(len(marker_info)):
        x, y, w, h, info = marker_info[i]
        markers.append(MarkerInfo(x, y, w, h, info))

# === Line PID ===
def line_pid_control(error, prev_error, integral, l_kp, l_ki, l_kd):
    derivative = error - prev_error
    integral += error
    control = l_kp * error + l_ki * integral + l_kd * derivative
    return control, integral

# === Main Logic ===
def run_robot_main(target_shelf_marker, target_product_marker):
    robomaster.config.Local_IP_STR = "192.168.2.36"
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')

    ep_chassis = ep_robot.chassis
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera

    l_kp, l_ki, l_kd = 0.5, 0.01, 0.1
    integral, prev_error = 0.0, 0.0

    ep_camera.start_video_stream(display=False)
    ep_vision.sub_detect_info(name="line", color="red", callback=on_detect_line)
    ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)

    try:
        while True:
            img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)

    
            if not line_type_detected:
                if line:
                    center_x = line[0]._x * 1280
                    error = 640 - center_x
                    control, integral = line_pid_control(error, prev_error, integral, l_kp, l_ki, l_kd)
                    prev_error = error
                    ep_chassis.drive_speed(x=0.3, y=0, z=-control, timeout=0.1)
                else:
                    ep_chassis.drive_speed(x=0, y=0, z=0)
            else:
                print("[Robot] พบเส้น type 2 → หยุดเพื่อสแกน marker ชั้นวาง")
                ep_chassis.drive_speed(x=0, y=0, z=0)
                time.sleep(1.5)

                shelf_matched = any(m.text == target_shelf_marker for m in markers)
                if shelf_matched:
                    print(f"[Robot] พบ marker ชั้นวาง {target_shelf_marker}")
                    break
                else:
                    print(f"[Robot] Marker ชั้นวางไม่ตรง → เดินหน้าต่อ")
                    line_type_detected = False
                    time.sleep(0.5)

        print("[Robot] 🔍 ตรวจจับ marker สินค้า...")
        while True:
            img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            found = any(m.text == target_product_marker for m in markers)
            if found:
                print(f"[Robot] พบสินค้า: {target_product_marker} → หยุดทำงาน")
                ep_chassis.drive_speed(x=0, y=0, z=0)
                ep_robot.play_sound(robot.SOUND_ID_1A).wait_for_completed()
                break
            else:
                ep_chassis.drive_speed(x=0.2, y=0, z=0)
                time.sleep(0.2)

            cv2.imshow("Detecting", img)
            cv2.waitKey(1)

    finally:
        ep_vision.unsub_detect_info(name="line")
        ep_vision.unsub_detect_info(name="marker")
        ep_camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()
