#----------------------------------------------------------------------------
# Ocean 351 Temperature sensor deployment code
#
# Sensor field deployment code
# - Samples and save temperatures data with a time stamp
# - Saves a .csv data file, posts to ThingSpeak if WiFi connection is available
# 
#----------------------------------------------------------------------------



"""
How to use this code:

To sample continuously with sleep cycle connect Pin 16 to RST
To download data files and not enter sleep cycle, connect Pin 16 to GND

This code establishes the function sample_temp() which takes three arguments:
- sleep_flag          
- sample_interval_sec               

"sleep_flag" sets whether your sensor sleeps: 1 --> sleep; 0 --> no sleep (ex:sleep_flag = 0)
"sample_interval_sec" sets the number of seconds between desired temp readings (ex: sample_interval_sec=5*60)

default parameters are sleep_flag=0,sample_interval_sec=30, these get overwritten with the parameters you set in main.py


Example usage (see below for additional parameter options):

>>>from field_deployment import sample_temp
>>>sample_temp()

These parameters should be set/modified in main.py to trigger automatic sampling upon wakeup

Use Pin 16 to control sleep mode:
    When Pin 16 is connected to RST, Pin 16 is pulled high. This condition must be met for the sensor to sleep
    If Pin 16 is disconnected from RST and connected to a GND pin, the sensor does not go to sleep.
"""
#from machine import Pin
#import time

#p12 = Pin(12, Pin.IN)

def pin_handler(arg,):
    global counter
    counter+=1
    print(counter)

def runCounter(timeToRun=15):
    from machine import Pin
    import time
    p12 = Pin(12, Pin.IN)
    starttime = time.time()
    global counter
    counter = 0
    while time.time() < starttime + timeToRun:
        p12.irq(handler = pin_handler, trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING)
    
    rotations = counter
    print("total count", rotations)
    return rotations

#r = runCounter(30) 

def sample(sleep_flag=0,sample_interval_sec=15):
    
    from machine import Pin, I2C, RTC, DEEPSLEEP, deepsleep
    import time
    import urtc
    import ms5803
    from time import sleep_ms
    from machine import Pin, I2C, RTC, DEEPSLEEP, deepsleep

    print("starting sampling")
    # Assign Pin 16
    p16=Pin(16, mode=Pin.IN)

    # Check if Pin 16 is pulled low, if yes, put the instrument to sleep, if not keep going
    if p16.value()==0:
        sleep_flag=0

    
    # -------------------------------------------------------------------------------
    # Set up the DS3231 external RTC (clock)
    # -------------------------------------------------------------------------------
    
    p15 = Pin(15, Pin.OUT)  # Assign Pin 15 to power the DS3231 RTC
    p15.value(1)            # Set Pin 15 high

    i2c = I2C(scl = Pin(5), sda = Pin(4))   # Initalize the I2C pins
    rtc3231 = urtc.DS3231(i2c)              # Assign the DS3231


    # -------------------------------------------------------------------------------
    # Set up the Hall Effect sensor
    # -------------------------------------------------------------------------------
    
    p12 = Pin(12, Pin.IN)  # Assign Pin 12 to power the DS18B20

    r = runCounter(15)

    # -------------------------------------------------------------------------------
    # Set up the Pressure sensor
    # ------------------------------------------------------------------------------

    water_pressure = ms5803.read(i2c=i2c, address = 118)

    p = water_pressure[0]
    t = water_pressure[1]


    # -------------------------------------------------------------------------------
    # Create the sleep cycle for the instrument
    # -------------------------------------------------------------------------------   
    
    # Initialize onboard RTC
    rtc = RTC()

    # Set an interupt to wake up at the next sampling period
    rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, 1000*sample_interval_sec) 
    sleep_ms(1000)      # sleep for 1 s


    #-------------------------------
    # Sample and save data
    #-------------------------------
    d = rtc3231.datetime()

    # Create a formatted time stamp for the collected data
    date = str(d.year) + '/' + str(d.month) + '/' + str(d.day) + ' ' + str(d.hour) + ':' + str(d.minute) + ':' + str(d.second)

    # temp sensor reading and saving procedure
    print("rotations", r, "date", date, "press", p, "temp", t )
    datafile=open("field_data.csv",'a')
    datafile.write(str(date) + "," + str(r) + "," + str(p) + "," + str(t) + "\n")

    datafile.close()
    sleep_ms(1000)      # Sleep for 1 sec

    print("\n")  


    #----------------------------------
    # Close connections and hardware, and prepare to sleep 

    # Turn off power to clock
    p15.value(0)

    # sleep for 5 sec
    sleep_ms(5000)

    # If in sleep_flag=1 and Pin 16 is connected to RST, go into deepsleep until the next sampling time.
    # If in sleep_flag=0 or Pin 16 is connected to GND, stop and wait for user to do something  
    if sleep_flag==1 and p16.value()==1:
        print('sleeping in 0.5 seconds...')
        sleep_ms(500)
        deepsleep()


#sample()`