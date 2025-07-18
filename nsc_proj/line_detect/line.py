import cv2
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


line = []


def on_detect_line(line_info):
    number = len(line_info)
    line.clear()
    line_type = line_info[0]
    #print('line_type', line_type)
    for i in range(1, number):
        x, y, ceta, c = line_info[i]
        line.append(PointInfo(x, y, ceta, c))
        print('line_type', line_info[0])



if __name__ == '__main__':
    robomaster.config.Local_IP_STR = "192.168.128.5"
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')
    
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera

    ep_camera.start_video_stream(display=False)
    result = ep_vision.sub_detect_info(name="line", color="red", callback=on_detect_line)

    while True:

        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        for j in range(0, len(line)):
            cv2.circle(img, line[j].pt, 3, line[j].color, -1)
            

            
        cv2.imshow("Line", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    result = ep_vision.unsub_detect_info(name="line")
    ep_camera.stop_video_stream()
    ep_robot.close()