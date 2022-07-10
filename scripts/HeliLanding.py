#! /usr/bin/env python
# Import ROS.
from asyncio.windows_events import NULL
import rospy
# Import the API.
from iq_gnc.py_gnc_functions import *
# To print colours (optional).
from iq_gnc.PrintColours import *
import cv2
import numpy as np
import re


def findingCircle(cap):
    
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name

    if (cap.isOpened()== False):
        print("Error opening video stream or file")

    if(cap.isOpened()):
        # Capture frame-by-frame
        
        ret, frame = cap.read()

        # 흑백 영상으로 변환(원을 검출하기 위해)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 허프 변환 함수가 노이즈에 민감하기 때문에 가우시안 블러로 노이즈 제거
        blr = cv2.GaussianBlur(gray, (0, 0), 1)
        

        # 허프 변환 원 검출
        # 트랙바를 이용한 테스트로 파라미터 값 결정
        circles = cv2.HoughCircles(blr, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=40, minRadius=30, maxRadius=70)
        #실제 테스트를 바탕으로 minRadius를 산출해야할 듯합니다.
        
        if circles is not None: # 원이 검출 됬으면
            #for i in range(circles.shape[1]): # 원의 개수 만큼 반복문
            cx, cy, radius = circles[0][0] # 중심좌표, 반지름 정보 얻기
                #cv2.circle(dt, (cx, cy), int(radius), (0, 0, 255), 2, cv2.LINE_AA) # 얻은 정보로 원 그리기
                #print(cx, cy) #원 중심 좌표
            return cx, cy
        else :
            return -1, -1

def findingHeliYolo(cap):
    frame = cap.read()


    crx = 0
    cry = 0
    return crx, cry



def main():

    # Initialise ROS node
    rospy.init_node("Landing")
    

    # Create an object for the API.
    drone = gnc_api()
    # Wait for FCU connection.
    drone.wait4connect()
    # Wait for the mode to be switched.
    drone.wait4start()
    # Create local reference frame.
    drone.initialize_local_frame()
    # Request takeoff with an altitude of 10m.
    drone.takeoff(10)

    # Specify some waypoints
    wps = []
    # Amount to move in the y-direction (local frame) in the snake like pattern.
    spacing = 10.0
    # No of times the snake like pattern needs to repeat.
    rows = 5
    # Amount to move in the x-direction (local frame) in the snake like pattern.
    drange = 50.0

    for i in range(rows):
        # Creating the snake like pattern and pushing it to the waypoints list.
        row = i * 2
        x = row * spacing
        y = 0
        z = 10
        psi = 0
        wps.append([x, y, z, psi])

        x = row * spacing
        y = drange
        z = 10
        psi = 0
        wps.append([x, y, z, psi])

        x = (row+1) * spacing
        y = drange
        z = 10
        psi = 0
        wps.append([x, y, z, psi])

        x = (row+1) * spacing
        y = 0
        z = 10
        psi = 0
        wps.append([x, y, z, psi])

    # Specify control loop rate. We recommend a low frequency to not over load the FCU with messages. Too many messages will cause the drone to be sluggish.
    rate = rospy.Rate(2)
    i = 0

    """
    while i < len(wps):
            drone.set_destination(
                x=wps[i][0], y=wps[i][1], z=wps[i][2], psi=wps[i][3])
            rate.sleep()
            if drone.check_waypoint_reached():
                i += 1
        
            break
    """ 
    #비행이 끝나고 착륙장 근처에 도착한 시점
    count = 0
    cap = cv2.VideoCapture(0)
    w = 640
    h = 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, h)

    isCenter = False
    while count < 7:
        cx, cy = findingCircle(cap)
        crx, cry = findingHeliYolo(cap)

        if cx == -1 and cy == -1:
            continue
        posi = drone.get_current_location()
        isCenterX = False
        isCenterY = False

        vec = [[posi.x + 1, posi.x, posi.x - 1], [posi.y + 1, posi.y, posi.y -1], [posi.z + 1, posi.z, posi.z - 1]]

        if posi.x < cx - 5 :
            drone.set_destination(x = vec[0][2], y= vec[1][1], z= vec[2][1], psi = 0)
        elif posi.x > cx + 5 :
            drone.set_destination(x = vec[0][0], y= vec[1][1], z= vec[2][1], psi = 0)
        else :
            isCenterX = True

        if posi.y < cy - 5 :
            drone.set_destination(x = vec[0][1], y= vec[1][0], z= vec[2][1], psi = 0)
        elif posi.y > cy + 5 :
            drone.set_destination(x = vec[0][1], y= vec[1][2], z= vec[2][1], psi = 0)
        else :
            isCenterY = True

        if isCenterX and isCenterY:
            drone.set_destination(x = vec[0][1], y= vec[1][1] , z = vec[2][2], psi = 0)
            count += 1

        #드론 포지션 가져오기

        
    drone.land()
   
    # Shutdown node.
    rospy.signal_shutdown()
    
    cap.release()
    cv2.destroyAllWindows()


# Driver code.
if __name__ == '__main__':
    try:
        main()
        # Used to keep the node running.
        rospy.spin()
    except KeyboardInterrupt:
        rospy.signal_shutdown("KeyboardInterrupt")
        exit()
