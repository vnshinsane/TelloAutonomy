import cv2
import numpy as np
from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()

w, h = 360, 240
fbRange = [6200, 6800]
pid = [0.55, 0.2, 0]
pError = 0
frame_count = 0

faceCascade = cv2.CascadeClassifier('Resources/haarcascade_frontalface_default.xml')
if faceCascade.empty():
    raise FileNotFoundError("Could not load Haar cascade xml file")

def findFace(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 6, minSize = (40, 40))

    myFaceListC = []
    myFaceListArea = []

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cx = x+w // 2
        cy = y+h // 2
        area = w*h
        cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    return img, [[0, 0] ,0]

def trackFace(me, info, w, h, pid, pError):
    area = info[1]
    x, y = info[0]
    fb = 0

    if area == 0:
        me.send_rc_control(0, 0, 0, 0)
        return 0

    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -75, 75))

    vError = h // 2 - y
    ud = int(np.clip(0.3 * vError, -50, 50))

    if abs(vError) < 15:
        ud = 0

    if abs(error) < 20:
        speed = 0
    elif abs(speed) < 40:
        speed = 40 if speed > 0 else -40


    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -40
    elif area < fbRange[0] and area != 0:
        fb = 40

    print("x", x, "y", y, "speed", speed, "ud", ud, "area", area, "fb", fb, "error", error)

    me.send_rc_control(0, fb, ud, speed)
    return error

airborne = False

try:
    me.streamon()
    frame_reader = me.get_frame_read()
    sleep(2)

    me.takeoff()
    airborne = True
    sleep(2)

    me.send_rc_control(0, 0, 0, 0)
    sleep(2)

    while True:
        img = frame_reader.frame

        if img is None:
            me.send_rc_control(0, 0, 0, 0)
            continue

        img = cv2.resize(img,(w, h))
        img = cv2.convertScaleAbs(img, alpha = 1.2, beta = 20)
        img, info = findFace(img)

        pError = trackFace(me, info, w, h, pid, pError)

        frame_count += 1
        if frame_count % 10 == 0:
            print("Centre", info[0], "Area", info[1])
        cv2.imshow('Tello Face Tracking',img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    try:
        me.send_rc_control(0, 0, 0, 0)
        if airborne:
             me.land()

        me.streamoff()

    except Exception as e:
        print(f"Shutdown errror: {e}")

cv2.destroyAllWindows()
