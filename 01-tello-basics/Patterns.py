from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()

print(me.get_battery())

def fly_square(side_length=100, direction="clockwise"):
    for _ in range(4):
        me.move_forward(side_length)

        if direction == "clockwise":
            me.rotate_clockwise(90)
        else:
            me.rotate_counter_clockwise(90)

#VELOCITY CONTROL VERSION OF SAME FLY SQUARE SCRIPT, JUST DOESN'T USE IMU BECAUSE I HAVEN'T CALIBRATED YET
def fly_squared(speed=20, side_time=1.5):
    for _ in range(4):

        me.send_rc_control(0, speed, 0, 0)
        sleep(side_time)

        me.send_rc_control(0, 0, 0, 0)
        sleep(0.3)

        me.send_rc_control(0, 0, 0, 50)
        sleep(1.0)

        me.send_rc_control(0, 0, 0, 0)
        sleep(0.3)

def fly_triangle(side_length=100):
    for i in range(3):
        me.move_forward(side_length)
        me.rotate_clockwise(120)
        sleep(0.2)

def fly_rectangle(long_side=50, short_side=30):
    side_lengths = (long_side, short_side, long_side, short_side)

    for length in side_lengths:
        me.move_forward(length)
        me.rotate_clockwise(90)

try:

    me.takeoff()
    sleep(3)

    fly_square()
    #fly_triangle()
    #fly_rectangle()

    me.land()

except Exception as e:
    print(e)
    me.land()

