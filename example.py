#!/usr/bin/env python3

import hp9800 

acmeter_port = '/dev/ttyUSB2'

 #####################################################################
 #                      Main programm
 #####################################################################
if __name__ == "__main__":
  acmeter_device = hp9800.acmeter(port = acmeter_port)
  
  power_ac = round(acmeter_device.getPower(),1)
  print("Power consumtion: " + str(power_ac) + "W")
