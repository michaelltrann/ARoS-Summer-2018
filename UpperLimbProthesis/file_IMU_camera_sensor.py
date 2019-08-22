import logging
import sys
import time
import cv2
import os
from Adafruit_BNO055 import BNO055
import socket
import threading
import RPi.GPIO as GPIO
#####################################################
#Functions#
def ForceSensor():
    global k
    datastring = ''
    GPIO.output(cs,GPIO.LOW)                #Chip select low (active)
    for i in range(0,10):                   #Pulse clock 20 times (10 high,10 low)
        GPIO.output(clock,GPIO.HIGH)        #receive dataout for each rising edge of clock
        datastring = datastring + format(GPIO.input(dataout))   #Create bit string with values from dataout '1010101010'
        GPIO.output(clock,GPIO.LOW)
    GPIO.output(cs,GPIO.HIGH)               #Chip select high (inactive) when transfer complete

    value10bit = int(datastring,2)          #convert string of 10 bits to decimal value
    voltage = value10bit/conversionFactor   #convert adc value to voltage
    file3.write(str(k) + ',' + str(voltage) + '\n')
    #time.sleep(0.1)                         #time it takes between adc conversions is 21us, so 0.1sec is plenty of time
    return 

def IMU():
    #current = 0
    #current = time.time()
    global k
    k += 1
    # Read the Euler angles for heading, roll, pitch (all in degrees).
    heading, roll, pitch = bno.read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = bno.get_calibration_status()


    # Accelerometer data (in meters per second squared):
    xa,ya,za = bno.read_accelerometer()
    # Linear acceleration data (i.e. acceleration from movement, not gravity--
    # returned in meters per second squared):
    xg,yg,zg = bno.read_gyroscope()

    writeStr = str(k) + ","  + str(roll) + "," + str(pitch) + "," + str(heading) + "," + str(xa) + "," + str(ya) + "," + str(za) + "," + str(xg) + "," + str(yg) + "," + str(zg)  
    file.write(writeStr + "\n")
    print('Sys:{}, Gyro:{}, Acc:{}'.format(sys,gyro,accel))
    #print(1/(time.time()-current))
    return

def Camera():
    #current = 0 
    while True:
        #current = time.time()
        ret, frame = cap.read()     
        name = "view.jpg"
        #Include Clarity Condition
        cv2.imwrite(name,frame)
        cv2.imshow('frame',frame)                               #display webcam window
        if cv2.waitKey(1) & 0xFF == ord('q'):                   #press q to close the webcam
            break
        #print(1/(time.time()-current))
    cap.release()
    cv2.destroyAllWindows()
    return
######################################################
##Camera and IMU Setup##
cap = cv2.VideoCapture(0)
#RPI vin to 3.3v, gnd to gnd, SDA to pin 10 (RXD), SCL to pin 8 (TXD)
bno = BNO055.BNO055(serial_port='/dev/ttyS0')

# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')
# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')
k = 0

try:
    file = open("imudata.csv","a+")
except IOError:
    file = open("imudata.csv","w+")
    print("New file")

try:
    file1 = open("k_data.txt","r")
    k = int(file1.readlines()[0])
    file1.close()
except:
    pass
####################################################
##Force Sensor and TCP Server setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

cs = 29
dataout = 31
clock = 33
conversionFactor = 1023/5

GPIO.setup(cs, GPIO.OUT)                    
GPIO.setup(dataout, GPIO.IN)                #data from adc to rpi
GPIO.setup(clock, GPIO.OUT)

GPIO.output(cs,GPIO.HIGH)                   #Chip select high at start up
GPIO.output(clock,GPIO.LOW)                 #clock low at start up

try:
    file3 = open("forcedata.csv",'a+')
except IOError:
    file3 = open("forcedata.csv",'w+')
#####################################################
time.sleep(2)

cam_thread = threading.Thread(target=Camera, args=())
cam_thread.start()
try:
    while True:
        imu_thread = threading.Thread(target=IMU, args=())
        sensor_thread = threading.Thread(target=ForceSensor, args=())
        imu_thread.start()
        sensor_thread.start()
        imu_thread.join()
        sensor_thread.join()
        time.sleep(0.0001)
    
except KeyboardInterrupt:
    file2 = open("k_data.txt","w+")
    file2.write(str(k))
    file2.close()    
    file.close()
    file3.close()
    print('End')


