from robomaster import robot
import robomaster


if __name__ == '__main__':
    robomaster.config.Local_IP_STR = "192.168.128.5" # แก้ IP ตามหุ่นยนต์
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')

    ep_version = ep_robot.get_version()
    print("Robot Version: {0}".format(ep_version))

    ep_robot.close()