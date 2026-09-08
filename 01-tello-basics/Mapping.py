from KeyboardControl import me, getKeyboardInput
from time import sleep
import numpy as np
import cv2
import math

#when true, map will work but drone won't, when false, both drone will fly and map will form
TEST_MODE = True

x, y = 500, 500
yaw = 0

points = [(x, y)]

forward_speed = 11.7
angular_speed = 36
interval = 0.1

distance_interval = forward_speed * interval
angle_interval = angular_speed * interval

def update_position(fb, lr, yv):
    global x, y, yaw

    #increase if rotating clockwise and decrease if rotating anticlockwise drone heading
    if yv> 0:
        yaw += angle_interval
    elif yv < 0:
        yaw -= angle_interval

    #keeps heading degrees between 0 and 359
    #e.g. 361 degrees becomes 1 degree
    yaw %= 360

    #convert to radians
    heading = math.radians(yaw)

    #assume drone hasn't moved
    forward_distance = 0
    sideways_distance = 0

    #check if forwards or backwards
    if fb > 0:
        forward_distance = distance_interval
    elif fb < 0:
        forward_distance = -distance_interval

    #check if drone moved left or right
    if lr > 0:
        sideways_distance = distance_interval
    elif lr < 0:
        sideways_distance = -distance_interval

    #convert drone relative movement into world coordinates
    #calculate how much x coordinate has changed
    delta_x = (forward_distance * math.cos(heading) - sideways_distance * math.sin(heading))

    #calculate how much y coordinate has changed
    delta_y = (forward_distance * math.sin(heading) + sideways_distance * math.cos(heading))

    #append estimated position
    x += delta_x
    y += delta_y

def get_current_point():
    point_x = int(x)
    point_y = int(y)

    #return current map position as a tuple
    return point_x, point_y

def store_current_point():
    current_point = get_current_point()

    #command to store point but only if its different from previous one
    if current_point != points[-1]:
        points.append(current_point)

def draw_map():
    #create black 1000x1000 bgr image
    img = np.zeros((1000, 1000, 3), dtype = np.uint8)

    #draw a small red circle at every stored position
    for point in points:
        cv2.circle(img, point, 4, (0, 0, 255), cv2.FILLED)

    current_point = points[-1]

    #draw drone current position as larger green circle
    cv2.circle(img, current_point, 7, (0, 255, 0), cv2.FILLED)

    #convert current pixel position into metres relative to the centre
    x_metres = (current_point[0] -500) / 100
    y_metres = (500 - current_point[1]) / 100

    cv2.putText(img, f"x: {x_metres:.2f} m, y: {y_metres:.2f} m", (20, 40),  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

    return img

try:
    while True:
        vals = getKeyboardInput()

        lr = vals[0]
        fb = vals[1]
        ud = vals[2]
        yv = vals[3]

        #map will react drone will stay hovering
        if not TEST_MODE:
            me.send_rc_control(lr, fb, ud, yv)

        update_position(fb, lr, yv)

        store_current_point()

        #create latest map image and display in an OpenCV window
        map_image = draw_map()
        cv2.imshow("Tello Mapping", map_image)

        #wait breifly so OpenCV can refresh its window, press escape while OpenCV window selected to stop
        if cv2.waitKey(1) & 0xFF == 27:
            break

        sleep(interval)

except KeyboardInterrupt:
    print("Program Ended")

finally:
    if not TEST_MODE:
        try:
            me.send_rc_control(0, 0, 0, 0)
        except Exception as e:
            print(f"Could not stop drone movement: {e}")

    cv2.destroyAllWindows()



