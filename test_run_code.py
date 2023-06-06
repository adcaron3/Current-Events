#------------------
# import functions
#------------------
from machine import Pin, I2C
import time
import urtc
import ms5803

p12 = Pin(12, Pin.IN)

#-----------------
#rotation counter
#-----------------

def pin_handler(arg,):
    global counter
    counter+=1
    print(counter)

def runCounter(timeToRun=10):
    starttime = time.time()
    global counter
    counter = 0
    while time.time() < starttime + timeToRun:
        p12.irq(handler = pin_handler, trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING)
        
    rotations = counter
    print("total count", rotations)
    return rotations
    #print("total count", rotations)

r = runCounter(10)
# assign clock pins & pressure pins
i2c = I2C(scl = Pin(5), sda = Pin(4)) # assigns the I2C connection
rtc = urtc.DS3231(i2c) # assigns the RTC, an I^2 device

#--------------------------------
#pressure and temperture reading
#--------------------------------

water_press = ms5803.read(i2c=i2c, address = 118)

p = water_press[0]
t = water_press[1]

#--------------------------
#rotation and clock reading
#--------------------------

#r = runCounter(10)
d = rtc.datetime()

date = str(d.year) + '/' + str(d.month) + '/' + str(d.day) + ' ' + str(d.hour) + ':' + str(d.minute) + ':' + str(d.second)

print("r", r, "date", date, "press", p, "temp", t)
datafile=open("field_data.csv",'a')
datafile.write(str(date) + "," + str(r) + "," + str(p) + "," + str(t) + "\n") # save time and temp to data file
datafile.close()

