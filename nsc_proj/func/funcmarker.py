import cv2
import robomaster
from robomaster import robot
from robomaster import vision
import time

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

# PID con. for marker
def marker_pid_control(error):
    global previous_error, integral
    integral += error
    derivative = error - previous_error
    output = m_kp * error + m_ki * integral + m_kd * derivative
    previous_error = error
    return output

def on_detect_marker(marker_info):
    number = len(marker_info)
    markers.clear()
    for i in range(0, number):
        x, y, w, h, info = marker_info[i]
        markers.append(MarkerInfo(x, y, w, h, info))
        print("'marker:{0}".format(info))


# varriable for marker
markers = []
#marker_soi = False
frame_center_x = 640


# PID con. for marker
m_kp = 0.8
m_ki = 0.001
m_kd = 0.05
previous_error = 0.0
integral = 0.0


if __name__ == '__main__':
    robomaster.config.Local_IP_STR = "192.168.2.36"
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')

    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_chassis = ep_robot.chassis
    
    ep_camera.start_video_stream(display=False)
    result = ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)

    for i in range(0, 400):
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        for marker in markers:
            cv2.rectangle(img, marker.pt1, marker.pt2, (255, 255, 255))
            cv2.putText(img, marker.text, marker.center, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
       
        if markers:
            target_marker = next((m for m in markers if m.text == "target_marker"), None)
            if target_marker:
                marker_x = target_marker.center[0]
                error = frame_center_x - marker_x
                adjustment = marker_pid_control(error)
                ep_chassis.drive_speed(x=0, y=-(adjustment / 1280), z=0)
                time.sleep(1)
                print(f"  error: {error}")

                if abs(error) < 30:
                    ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()
                    ep_robot.play_sound(robot.SOUND_ID_1A).wait_for_completed()
                else:
                    ep_chassis.drive_speed(x=0, y=0.2, z=0, timeout=1)
                    
        cv2.imshow("Markers", img)
        cv2.waitKey(1)

    result = ep_vision.unsub_detect_info(name="marker")
    cv2.destroyAllWindows()
    ep_camera.stop_video_stream()
    ep_robot.close()
