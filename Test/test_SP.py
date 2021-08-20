# from logging import root
import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/Follow_darius/robotdetection/")
from Robot_Detection_Manager.Robot_Detection_Manager import Robot_Detection_Manager

robot_users = Robot_Detection_Manager.get_distinct_robot_user()
# print("Type of robot_users = %s" % type(robot_users)) # class List
# print("robot = %s" % len(robot_users[0])) # 63333
# robot_users = robot_users[0]
# robot_users = [x[0] for x in robot_users]
# top = 10
# print("The first %s users = %s" % (top, robot_users[:top]))
print("robot_users = ", robot_users)
