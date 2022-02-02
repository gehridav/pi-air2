#!/usr/bin/env python
########################################################################
# Calibration and read of the CO2 sensor MH-Z16
# according to the datasheet : http://www.seeedstudio.com/wiki/images/c/ca/MH-Z16_CO2_datasheet_EN.pdf
# output value directly in ppm
'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
'''
#
########################################################################
import os
import serial, time
import math
import sys
import struct
import binascii

#co2 sensor
#use an external usb to serial adapter
#ser = serial.Serial('/dev/ttyUSB0',  9600, timeout = 1)	#Open the serial port at 9600 baud

#To open the raspberry serial port
ser = serial.Serial('/dev/serial0',  9600, timeout = 1)	#Open the serial port at 9600 baud

#init serial
ser.flush()


############# carbon dioxid CO2 #####################
class CO2:
#inspired from c code of http://www.seeedstudio.com/wiki/Grove_-_CO2_Sensor
#Gas concentration= high level *256+low level
    
    cmd_zero_sensor = "\xff\x87\x87\x00\x00\x00\x00\x00\xf2"
    cmd_span_sensor = "\xff\x87\x87\x00\x00\x00\x00\x00\xf2"
    cmd_get_sensor = "\xff\x01\x86\x00\x00\x00\x00\x00\x79"
    
    def verify_checksum(bytes):
        if len(bytes) != 9:
            return False
        sum = 0
        for i in range(1, 8):
            sum += bytes[i]
        sum = sum % 256
        checksum = 255 - sum + 1

        return bytes[8] == checksum
    
    def read(self):
        try:
          while True:
                ser.write(bytearray(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'))
                rcv_data = ser.read(9)
                if not CO2.verify_checksum(rcv_data):
                    print("Checksum error from received: `{}'".format(binascii.hexlify(rcv_data)))
                high_level = rcv_data[2] 
                low_level = rcv_data[3] 
                #temp_co2  =  struct.unpack('B',CO2.inp[4])[0] - 40
                #print("Temp: {}".format(rcv_data[4]))
                #output in ppm
                conc = high_level*256+low_level
                return conc

        except IOError:
                return -1

    def calibrateZero(self):
        try:
             ser.write(CO2.cmd_zero_sensor.encode())
             print("CO2 sensor zero calibrated")

        except IOError:
                print("CO2 sensor calibration error")

    def calibrateSpan(self):
        try:
          while True:
                #ser.write(CO2.cmd_zero_sensor.encode())
                print("CO2 sensor span calibrated")
                break

        except IOError:
                print("CO2 sensor calibration error")



########################################################################################################
#############   MAIN
########################################################################################################
# following the specs of the sensor :
# read the sensor, wait 3 minutes, set the zero, read the sensor
'''
c = CO2()

while True:
    try:
        #CO2 sensor calib
        print("wait 3 minutes to warm up CO2 sensor")
        #time.sleep(180)
        print("Read before calibration-->",c.read())

        print("calibrating...")
        co2 = c.calibrateZero()
        time.sleep(5)

        print("Read after calibration-->",c.read())

        print("DONE")
        break

    except IndexError:
        print("Unable to read")
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(0)
'''