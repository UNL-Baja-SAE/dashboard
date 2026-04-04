from machine import Pin
import time

hall = Pin(16, Pin.IN, Pin.PULL_UP)
counter = 0  

def rpm_trigger(c):
        global counter # Declare variable as global
        counter = counter + 1
        

hall.irq(trigger=Pin.IRQ_RISING, handler=rpm_trigger)
while True:
        sample_time = 1.5 #seconds
        time.sleep(sample_time)
        rpm = (counter/sample_time)*60
        print('Current RPM: ', rpm)
        counter = 0
        
  