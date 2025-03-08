#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

pub = None

def callback(data):
    rospy.loginfo("Received: %s", data.data)
    
    try:
        command = json.loads(data.data)

        handle_action(command)
    except json.JSONDecodeError as e:
        rospy.logerr("Error decoding JSON: %s", e)
    except KeyError as e:
        rospy.logerr("Missing key in JSON data: %s", e)

def handle_action(command):
    global pub
    twist = Twist()
    
    if command["action"] == "move":
        rospy.loginfo("Moving turtle")
        twist.linear.x = command["speed"]["linear"]["x"]
        twist.linear.y = 0
        pub.publish(twist)
        
        time_to_move = command["distance"] / command["speed"]["linear"]["x"]
        rospy.sleep(time_to_move)

        twist.linear.x = 0
        pub.publish(twist)
        
        rospy.loginfo("Rotating turtle")
        twist.angular.z = command["angular_speed"]["angular"]["z"]
        pub.publish(twist)
        


    else:
        rospy.logerr("Unknown action: %s", command.get("action"))

def listener():
    global pub
    rospy.init_node('control_listener', anonymous=True)
    
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    
    rospy.Subscriber("gpt_reply_to_user", String, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()

