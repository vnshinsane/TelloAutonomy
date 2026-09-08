from djitellopy import tello
import KeyPress as kp
from time import sleep

kp.init()
me=tello.Tello()
me.connect()

print(me.get_battery())
print(me.get_barometer())

def getKeyboardInput():
    kp.update()

    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kp.getKey("LEFT"): lr = -speed
    elif kp.getKey("RIGHT"): lr = speed

    if kp.getKey("UP"): fb = speed
    elif kp.getKey("DOWN"): fb = -speed

    if kp.getKey("w"): ud = speed
    elif kp.getKey("s"): ud = -speed

    if kp.getKey("a"): yv = -speed
    elif kp.getKey("d"): yv = speed

    if kp.getKey("q"):
        me.land()
        sleep(1)

    if kp.getKey("e"):
        me.takeoff()
        sleep(1)

    return [lr, fb, ud, yv]

def run_keyboard_control():
    while True:
        vals = getKeyboardInput()
        print(vals)
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
        sleep(0.1)

if __name__ == "__main__":
    run_keyboard_control()
