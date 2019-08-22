import logging
import sys
import time
import os
import threading
import time
import psutil
from Adafruit_BNO055 import BNO055

# initialize the connections
bno = BNO055.BNO055(serial_port='/dev/ttyS0')
# BeagleBone Black configuration with default I2C connection (SCL=P9_19, SDA=P9_20),
# and RST connected to pin P9_12:
# bno = BNO055.BNO055(rst='P9_12')


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

'''
 Configure Acc sampling rate to 125Hz and Gyro to 116Hz
'''
# Set operational mode to Config mode
bno.set_mode(0x00)
# Set Page ID to 1, where bandwidth registers are
bno._write_byte(0x07, 0x01)
# Set Acc bandwidth to 125Hz, range 16G
bno._write_bytes(0x08, [0x13])
# Set Gyro bandwidth to 116Hz, range 2000 dps
bno._write_bytes(0x0A, [0x10])
# Set back to Page ID 0
bno._write_byte(0x07, 0x00)
# Set operational mode to ACC and Gyro mode (NON Fusion)
bno.set_mode(0x05)

# Read
# Check operational mode
bno._read_byte(0x3D)    # 5
# Set Page ID to 1, where bandwidth registers are
bno._write_byte(0x07, 0x01)
# Check Acc configuration
bno._read_byte(0x08)    # 19
# Check Gyro configuration
bno._read_byte(0x0A)    # 16
# Set back to Page ID 0, allowing data reading
bno._write_byte(0x07, 0x00)
# Check page ID
bno._read_byte(0x07)    # 0

# Test code
print('before')
print(psutil.cpu_percent(1, 1))
t0 = time.time()
for k in range(0, 200):
    x, y, z = bno.read_accelerometer()
    gx, gy, gz = bno.read_gyroscope()
    if k == 50:
        print('after')
        print(psutil.cpu_percent(1, 1))
    #print('Acc: {}, {},{}'.format(str(x), str(y), str(z)))
    #print('Gyro: {}, {},{}'.format(str(gx), str(gy), str(gz)))
    time.sleep(1/10000)
    if k ==199:
        t1 = time.time()

print('{} readings of ACC and Gyro performed in {}s.'.format(str(200), str(t1-t0)))
