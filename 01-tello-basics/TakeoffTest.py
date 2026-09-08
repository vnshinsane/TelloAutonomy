from djitellopy import tello
from time import sleep

me = tello.Tello()
me.connect()
sleep(2)

battery = me.get_battery()

print("Battery:", battery)
print("Temperature:", me.get_temperature())
print("Pitch:", me.get_pitch())
print("Roll:", me.get_roll())
print("Yaw:", me.get_yaw())

if battery < 30:
    print("Batter < 30, too low for takeoff")

me.takeoff()
sleep(3)
me.land()