import cv2
from djitellopy import tello
from ultralytics import YOLO
import cvzone
import math
from time import sleep
import numpy as np

#SETUP
me = tello.Tello()
me.connect()

battery = me.get_battery()
print("Battery:", battery)

if battery < 30:
    print("Battery too low for flight")
    me.end()
    exit()

w, h = 1280, 720
fb = 0
pid = [0.45, 0.2, 0]
pError = 0
fbRange = [200000, 250000]

me.streamon()
frame_reader = me.get_frame_read()

target_id = None

model = YOLO('YOLO-weights/yolo11n.pt')

#PHASE 1: GET TELLO CAMERA FRAMES
def getFrame():
    img = frame_reader.frame
    if img is None:
        return None

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.resize(img, (1280, 720))

    return img

#PHASE 2: LOOK FOR PERSON IN EACH TELLO CAMERA FRAME AND SORT INTO BOXES WITH DIMENSIONS
def findPerson(img):
    results = model.track(img, stream=True, persist=True, tracker="botsort.yaml")
    global target_id

    for r in results:  # looking at each detected object and turning it into a box
        boxes = r.boxes

        for box in boxes:
            cls = int(box.cls[0])  # append class type into array
            current_id = int(box.id[0])

            # save first persons tracking ID once and then not ever again
            if cls == 0 and target_id is None:
                target_id = current_id

            if cls == 0 and target_id == current_id: # person = id class 0 and target_id is id of first persons box
                # Bounding Box construction
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                width = x2 - x1
                height = y2 - y1

                centre_x = (x1 + x2) // 2
                centre_y = (y1 + y2) // 2
                area = width * height
                print("Area: ", area)

                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # print(x1, y1, x2, y2 corners of bounding box)

                conf = math.ceil((box.conf[0] * 100)) / 100  # print confidence level
                cvzone.putTextRect(img, f'person {conf}', (x1, y1 - 10), 2)

                return True, centre_x, centre_y, area

    return False, 0, 0, 0

def scanPerson(pError):
    if pError < 0:
        me.send_rc_control(0, 0, 0, -15)

    elif pError > 0:
        me.send_rc_control(0, 0, 0, 15)

    else:
        me.send_rc_control(0, 0, 0, 15)

def trackPerson(centre_x, centre_y, area, pError):
    error = centre_x-w//2 #horizontal difference between person centre and frame centre
    Verror = h//2 - centre_y #vertical difference
    fb_speed = 0

    yaw_speed = pid[0] * error + pid[1] * (error - pError)
    yaw_speed = int(np.clip(yaw_speed, -40, 40))

    ud_speed = 0.3 * Verror
    ud_speed = int(np.clip(ud_speed, -40, 40))

    if area > fbRange[0] and area < fbRange[1]:
        fb_speed = 0
    elif area > fbRange[1]:
        fb_speed = -20
    elif area < fbRange[0] and area != 0:
        fb_speed = 20

    if abs(error) < 100:
        yaw_speed = 0

    if abs(Verror) < 100:
        ud_speed = 0

    me.send_rc_control(0, fb_speed, ud_speed, yaw_speed)
    return error

#MAIN LOOP
def Operation():
    pError = 0

    try:
        me.takeoff()
        sleep(2)

        while True:
            #PHASE 1
            img = getFrame()
            if img is None:
                continue

            #PHASE 2
            person_found, centre_x, centre_y, area = findPerson(img)

            #PHASE 3
            if person_found and target_id is None:
                pError = trackPerson(centre_x, centre_y, area, pError)
            else:
                scanPerson(pError)

            #Display camera
            cv2.imshow('Tello View', img)

            #PRESS Q TO LAND
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        me.send_rc_control(0, 0, 0, 0)
        me.land()
        me.streamoff()
        cv2.destroyAllWindows()

Operation()

