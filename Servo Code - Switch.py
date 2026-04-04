from machine import Pin, PWM
import utime

min_ns = 500000
max_ns = 25000000

switch = Pin(16,Pin.IN,Pin.PULL_UP)
pwm = PWM(15)
pwm.freq(60)

while True:
    if switch.value() == 0:
        pwm.duty_ns(max_ns)
        print('4x4 engaged')
    else:
        pwm.duty_ns(min_ns)