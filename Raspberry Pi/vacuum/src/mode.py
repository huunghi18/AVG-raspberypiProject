#! /usr/bin/env python

# import ros stuff
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf import transformations
from std_msgs.msg import String
import time
#from std_srvs.srv import *

import math
t = 0
m = 0
k = 0
p = 0
q = 0
start = 0
process = 0
#active_ = False
pub_ = None
i = ' '
regions_ = {
        'right': 0,
        'fright': 0,
        'front': 0,
        'fleft': 0,
        'left': 0,
}
state_ = 0
state_dict_ = {
    0: 'find the wall',
    1: 'turn left',
    2: 'follow the wall',
    3: 'align path1',
    4: 'obstacle left',
    5: 'obstacle right',
    6: 'align path2',
    7: 'cliff front',
    8: 'cliff right',
    9: 'cliff left',
    10: 'turn right',
}

def change(msg):
    global i
    global k
    global q
    global start
    i = msg.data
    if i == '0':
	start = time.time()
    q = 0
    k = 0

def dung():
    msg = Twist()
    msg.linear.x = 0.0
    msg.angular.z = 0.0
    pub_.publish(msg)

def turn(msg):
    global obs
    global t
    global m
    global k
    global q
    global start
    global process
    if t == 0:	
        obs = msg.data
        if obs == '2' or obs == '3' or obs == '4' or obs == '5' or obs == '6' or obs == '7':
                t = 1
		m = 0
    if t == 1:
       if i == '7':	
    	 take_action1()
       if i == '6':
    	 take_action3()
       if i == '0':
	process = time.time()
	if q == 0:
    	 take_action3()
	 if (process - start) > 5.0:
		q = 1
		start = process
	if q == 1:
    	 take_action1()	 
	 if (process - start) > 15.0:
		q = 2
		start = process
		dung()

def take_action1():
    global obs
    global t
    global m	
    msg = Twist()
    linear_x = 0
    angular_z = 0

    if obs == '3' or obs == '4':
        change_state(4)
    if obs == '2':
        change_state(5)
    if obs == '5':
        change_state(7)
    if obs == '6':
        change_state(8)
    if obs == '7':
        change_state(9)

def clbk_laser(msg):
    global regions_
    global q
    global start
    global process 
    regions_ = {
#        'right':  min(min(msg.ranges[0:72]), 8),
        'fright': min(min(msg.ranges[270:319]), 8),
        'front':  min(min(msg.ranges[320:360]),min(msg.ranges[0:10]), 8),
        'fleft':  min(min(msg.ranges[11:70]), 8),
	'wall':  min(min(msg.ranges[295:305]), 8),
#        'left':   min(min(msg.ranges[289:360]), 8),
    }

    if t == 0:
       if i == '7':		
    	take_action()
       if i == '6':
    	 take_action2()
       if i == '0':
	process = time.time()
	if q == 0:
    	 take_action2()
	 if (process - start) > 5.0:
		q = 1
	if q == 1:
    	 take_action()	 
	 if (process - start) > 15.0:
		q = 2
		dung()

def take_action3():
    global obs
    global t
    global m	
    msg = Twist()
    linear_x = 0
    angular_z = 0
    
    if obs == '3' or obs == '4':
	if m < 20:
		linear_x = -0.1
       		angular_z = 0
		m = m + 1
	if m >= 20 and m < 60:
		linear_x = 0
       		angular_z = -0.3
		m = m + 1
	if m >= 60:
		t = 0
    if obs == '2':
	if m < 20:
		linear_x = -0.15
       		angular_z = 0
		m = m + 1
	if m >= 20 and m < 60:
		linear_x = 0
       		angular_z = 0.3
		m = m + 1
	if m >= 60:
		t = 0
    if obs == '5':
	if m < 30:
		linear_x = -0.2
       		angular_z = 0
		m = m + 1
	if m >= 30 and m <100:
		linear_x = 0
       		angular_z = -0.3
		m = m + 1
	if m >= 100:
		t = 0
    if obs == '6':
	if m < 30:
		linear_x = -0.2
       		angular_z = 0
		m = m + 1
	if m >= 30 and m <100:
		linear_x = 0
       		angular_z = 0.3
		m = m + 1
	if m >= 100:
		t = 0
    if obs == '7':
	if m < 30:
		linear_x = -0.2
       		angular_z = 0
		m = m + 1
	if m >= 30 and m <100:
		linear_x = 0
       		angular_z = -0.3
		m = m + 1
	if m >= 100:
		t = 0
    msg.linear.x = linear_x
    msg.angular.z = angular_z
    pub_.publish(msg)

def take_action2():
    global regions
    regions = regions_
    msg = Twist()
    linear_x = 0
    angular_z = 0
    
    state_description = ''


      
    if regions['front'] > 0.25 and regions['fleft'] > 0.25 and regions['fright'] > 0.25 :
        state_description = 'case 1 - nothing'
        linear_x = 0.15
        angular_z = 0
    elif regions['front'] < 0.25 and regions['fleft'] > 0.25 and regions['fright'] > 0.25 :
        state_description = 'case 2 - front'
        linear_x = 0
        angular_z = 0.5
    elif regions['front'] > 0.25 and regions['fleft'] > 0.25 and regions['fright'] < 0.25:
        state_description = 'case 3 - fright'
        linear_x = 0
        angular_z = 0.5
    elif regions['front'] > 0.25 and regions['fleft'] < 0.25 and regions['fright'] > 0.25:
        state_description = 'case 4 - fleft'
        linear_x = 0
        angular_z = -0.5
    elif regions['front'] < 0.25 and regions['fleft'] > 0.25 and regions['fright'] < 0.25:
        state_description = 'case 5 - front and fright'
        linear_x = 0
        angular_z = 0.5
    elif regions['front'] < 0.25 and regions['fleft'] < 0.25 and regions['fright'] > 0.25:
        state_description = 'case 6 - front and fleft'
        linear_x = 0
        angular_z = -0.5
    elif regions['front'] < 0.25 and regions['fleft'] < 0.25 and regions['fright'] < 0.25:
        state_description = 'case 7 - front and fleft and fright'
        linear_x = 0
        angular_z = 0.5
    elif regions['front'] > 0.25 and regions['fleft'] < 0.25 and regions['fright'] < 0.25:
        state_description = 'case 8 - fleft and fright'
        linear_x = 0.15
        angular_z = 0
    else:
        state_description = 'unknown case'
        rospy.loginfo(regions)

    rospy.loginfo(state_description)
    msg.linear.x = linear_x
    msg.angular.z = angular_z
    pub_.publish(msg)

def change_state(state):
    global state_, state_dict_
    if state is not state_:
        print 'Wall follower - [%s] - %s' % (state, state_dict_[state])
        state_ = state

def take_action():
    global regions_
    global k
    global p
    regions = regions_
    msg = Twist()
    linear_x = 0
    angular_z = 0
    
    state_description = ''
    
    d = 0.22
    
    if k == 0:
	if regions['front'] > d and regions['fleft'] > d and regions['fright'] > d:
		state_description = 'case 1 - nothing'
		change_state(0)
	elif regions['front'] < d and regions['fleft'] > d and regions['fright'] > d:
		state_description = 'case 2 - front'
		change_state(1)
		k = 1
	elif regions['front'] > d and regions['fleft'] > d and regions['fright'] < d:
		state_description = 'case 3 - fright'
		change_state(2)
		k = 1
	elif regions['front'] > d and regions['fleft'] < d and regions['fright'] > d:
		state_description = 'case 4 - fleft'
		change_state(0)
	elif regions['front'] < d and regions['fleft'] > d and regions['fright'] < d:
		state_description = 'case 5 - front and fright'
		change_state(1)
		k = 1
	elif regions['front'] < d and regions['fleft'] < d and regions['fright'] > d:
		state_description = 'case 6 - front and fleft'
		change_state(1)
		k = 1
	elif regions['front'] < d and regions['fleft'] < d and regions['fright'] < d:
		state_description = 'case 7 - front and fleft and fright'
		change_state(1)
		k = 1
	elif regions['front'] > d and regions['fleft'] < d and regions['fright'] < d:
		state_description = 'case 8 - fleft and fright'
		change_state(0)
	else:
		state_description = 'unknown case'
		rospy.loginfo(regions)
    if k == 1:
	if regions['wall'] > 0.22 :
		change_state(1)
	else :
		change_state(2)
		k = 2

    if k == 2:
	if regions['front'] < 0.21:
		change_state(1)
	else:
		if regions['wall'] < 0.2:
			change_state(3)
		elif regions['wall'] > 0.26:
			change_state(6)
		else :  
			change_state(2)
			p = 0

def find_wall():
    msg = Twist()
    msg.linear.x = 0.1
  #  msg.angular.z = -0.3
    return msg

def turn_left():
    msg = Twist()
    msg.angular.z = 0.4
    return msg

def turn_right():
    msg = Twist()
    msg.angular.z = -0.4
    return msg

def follow_the_wall():
    global regions_
    
    msg = Twist()
    msg.linear.x = 0.1
    return msg

def align_path1():
    global p
    msg = Twist()
    msg.linear.x = 0.06
    msg.angular.z = 0.6

    return msg

def align_path2():
    global p
    msg = Twist()
    msg.linear.x = 0.06
    msg.angular.z = -0.6

    return msg

def obstacle_left():
    global t
    global m	
    msg = Twist()
    msg.linear.x = 0
    msg.angular.z = 0

    if m < 8:
	msg.linear.x = -0.1
       	msg.angular.z = 0
	m = m + 1
    if m >= 8 and m < 25:
	msg.linear.x = 0
       	msg.angular.z = 0.4
	m = m + 1
    if m >= 25:
	t = 0

    return msg

def obstacle_right():
    global t
    global m	
    msg = Twist()
    msg.linear.x = 0
    msg.angular.z = 0

    if m < 8:
	msg.linear.x = -0.1
       	msg.angular.z = 0
	m = m + 1
    if m >= 8 and m < 25:
	msg.linear.x = 0
       	msg.angular.z = 0.4
	m = m + 1
    if m >= 25:
	t = 0

    return msg

def cliff_front():
    global t
    global m
    global k	
    msg = Twist()
    msg.linear.x = 0
    msg.angular.z = 0

    if m < 30:
	msg.linear.x = -0.1
       	msg.angular.z = 0
	m = m + 1
    if m >= 30 and m < 80:
	msg.linear.x = 0
       	msg.angular.z = 0.4
	m = m + 1
    if m >= 80:
	t = 0
	k = 0

    return msg

def cliff_right():
    global t
    global m
    global k	
    msg = Twist()
    msg.linear.x = 0
    msg.angular.z = 0

    if m < 30:
	msg.linear.x = -0.1
       	msg.angular.z = 0
	m = m + 1
    if m >= 30 and m < 60:
	msg.linear.x = 0
       	msg.angular.z = 0.4
	m = m + 1
    if m >= 60:
	t = 0
	k = 0

    return msg

def cliff_left():
    global t
    global m
    global k	
    msg = Twist()
    msg.linear.x = 0
    msg.angular.z = 0

    if m < 30:
	msg.linear.x = -0.1
       	msg.angular.z = 0
	m = m + 1
    if m >= 30 and m < 60:
	msg.linear.x = 0
       	msg.angular.z = -0.4
	m = m + 1
    if m >= 60:
	t = 0
	k = 0

    return msg

def main():
    global pub_
    
    rospy.init_node('rplidar_data', anonymous=True)
    
    pub_ = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
    
    sub = rospy.Subscriber('/scan', LaserScan, clbk_laser)

    sub = rospy.Subscriber('/sensor', String, turn)

    sub = rospy.Subscriber('/keyboard', String, change)    
   # srv = rospy.Service('wall_follower_switch', SetBool, wall_follower_switch)
    
    rate = rospy.Rate(20)
    while not rospy.is_shutdown():
   #     if not active_:
   #         rate.sleep()
   #         continue

       if i == '7' or q == 1:
        msg = Twist()
        if state_ == 0:
            msg = find_wall()
        elif state_ == 1:
            msg = turn_left()
        elif state_ == 2:
            msg = follow_the_wall()
        elif state_ == 3:
            msg = align_path1()
        elif state_ == 4:
            msg = obstacle_left()
        elif state_ == 5:
            msg = obstacle_right()
        elif state_ == 6:
            msg = align_path2()
        elif state_ == 7:
            msg = cliff_front()
        elif state_ == 8:
            msg = cliff_right()
        elif state_ == 9:
            msg = cliff_left()
        elif state_ == 10:
            msg = turn_right()
            pass
        else:
            rospy.logerr('Unknown state!')
        
        pub_.publish(msg)
        
       rate.sleep()

if __name__ == '__main__':
    main()
    
