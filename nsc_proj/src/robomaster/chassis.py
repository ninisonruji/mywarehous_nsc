from robomaster import robot
import robomaster
import time

if __name__ == '__main__':
    robomaster.config.Local_IP_STR = "192.168.128.5" # แก้ IP ตามหุ่นยนต์
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type='ap')
    ep_chassis = ep_robot.chassis

    x_val = 1.5
    y_val = 2.2
    z_val = 90


    ep_chassis.move(x=x_val, y=y_val, z=z_val, xy_speed=1).wait_for_completed()
    print("Move completed")
    print("Program stopped")

    ep_chassis.drive_speed(x = x_val, y=0, z=0, timeout=5)
    time.sleep(3)
    print("Move completed")
    print("Program stopped")
    
    ep_robot.close()
