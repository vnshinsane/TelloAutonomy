from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()

print(me.get_battery())

try:
    me.takeoff()

    me.send_rc_control(0, 50, 0, 0)
    sleep(1)
    me.send_rc_control(0, 0, 50, 0)
    sleep(1)
    me.send_rc_control(0, 0, 0, 40)

    me.land()

except Exception as e:
    print(e)
    me.land()

