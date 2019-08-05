# -*- coding:utf-8 -*-
#Created By Hower & Tom

#---------------------------import modules------------------------------
import RPi.GPIO as io
import time
import smbus
import math
import threading
import numpy as np
import sys
#----------------------------Port Config--------------------------------

# Set to the GPIO port of main relay
relay = 4
# Set to the GPIO port of the switch button
switchButton = 20
# Set to the GPIO port of the manual/auto mode button
manualAutoSwitch = 21

# Set to true if you also have a relay that turns off the inverter when unused
inverterRelayEnabled = False
# Set the port of inverter relay
inverterRelay = 26

# Set GPIO ports of dual 74HC595 display
# DS/DIO
displayDS = 17
# SHCP/SCK
displaySHCP = 22
# STCP/RCK
displaySTCP = 27

# Calibration data:
# Calculate adda using: divisor / multiplier * addaValue
addaDivisor = 12.6
addaMultiplier = 112

# Set to True to enable auto controlling of fan
fanEnabled = False
# Set to the GPIO where the relay controlling the fan is connected
fanPort = 19

# Set to True if you want to use LED in addition to the 8-digits display
ledEnabled = True
# LED representing whether manual mode is on
manualModeLED = 16
# LED representing whether the solar power is used
solarEnergyLED = 12
# LED representing whether the grid/city power is used
gridIndicator = 26

#----------------------------Initializing-------------------------------

#Setup I2C
address = 0x48

A0 = 0x40
A1 = 0x41
A2 = 0x42
A3 = 0x43

bus = smbus.SMBus(1)

#Setup BCM
io.setmode(io.BCM)

#Relay
io.setup(relay, io.OUT)

#Actual Switch Button
io.setup(switchButton,io.IN)

#Manual/Auto Swith Button
io.setup(manualAutoSwitch,io.IN)

#inverter Relay
if inverterRelayEnabled == True:
    io.setup(inverterRelay,io.OUT)

#Setup Display
DS = displayDS   #DIO

SHCP = displaySHCP #SCK

STCP = displaySTCP #RCK

io.setup(DS, io.OUT)
io.setup(STCP, io.OUT)
io.setup(SHCP, io.OUT)

io.output(STCP, False)
io.output(SHCP, False)

# Setup LEDs
if ledEnabled == True:
    io.setup(manualModeLED, io.OUT)
    io.setup(solarEnergyLED, io.OUT)
    io.setup(gridIndicator, io.OUT)

#Initialize Variable
city = 0
isCity = 5
volt = 100
isManual = False
solar = True

#set up array for moving average
movingAverage = []

for i in range(0,30):
    bus.write_byte(address,A0) 
    value = bus.read_byte(address)
    volt1 = round(12.4 / 207 * value, 2)
    movingAverage.append(volt1)

#Initializing Fan Control
def cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
        return float(f.read())/1000
#-------------------------------Display---------------------------------
def setBitData(data):
    # Send bit
    io.output(DS, data)
    # Activate Shift Register
    io.output(SHCP, False)
    io.output(SHCP, True)

# Preset function to display digits (1 - 9), 
# with optionn for dot point
def showDigit(num, showDotPoint):
     
    if (num == 0) :
        setBitData(not showDotPoint) # DP
        setBitData(True)  # G
        setBitData(False) # F
        setBitData(False) # E
        setBitData(False) # D
        setBitData(False) # C
        setBitData(False) # B
        setBitData(False) # A
    elif (num == 1) :
        setBitData(not showDotPoint)
        setBitData(True)
        setBitData(True)
        setBitData(True)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(True)
    elif (num == 2) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(False)
        setBitData(False)
    elif (num == 3) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(True)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
    elif (num == 4) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(True)
    elif (num == 5) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(False)
    elif (num == 6) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(False)
    elif (num == 7) :
        setBitData(not showDotPoint)
        setBitData(True)
        setBitData(True)
        setBitData(True)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(False)
    elif (num == 8) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
    elif (num == 9) :
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        
    elif (num == 10) :
        # Letter C
        setBitData(not showDotPoint) # DP
        setBitData(True)  # G
        setBitData(False) # F
        setBitData(False) # E
        setBitData(False) # D
        setBitData(True) # C
        setBitData(True) # B
        setBitData(False) # A
    elif (num == 11) :
        #Letter A
        setBitData(not showDotPoint)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        setBitData(True)
        setBitData(False)
        setBitData(False)
        setBitData(False)
        
def showLocation(location):
    for x in range(0,8):
        if x == location:
            setBitData(True)
        else:
            setBitData(False)
    
def showDigitWithLocation(num, showDotPoint, location):
    #io.output(STCP, False)
    
    showLocation(location)
    
    showDigit(num, showDotPoint)
    
    # Activate register lock to push bits into register
    io.output(STCP, True)
    io.output(STCP, False)

def displayVoltage():
    global volt
    global isCity
    while True:
        voltMultiplied = round(volt*100, 0)
        digits = 4
        divisor = 1000
        if voltMultiplied < 1000:
            digits = 3
            divisor = 100
        for i in range(1, digits + 1):
            digit = voltMultiplied % 10
            #print(digit)
            voltMultiplied = math.floor(voltMultiplied / 10)
            #print(voltMultiplied)
            showDot = False
            if i == 3:
                showDot = True
            showDigitWithLocation(digit, showDot, i - 1)
            time.sleep(0.001)
            
            showDigitWithLocation(isCity, False, 7)
            #showDigitWithLocation(isManual,False,5)
            if isManual == 0:
                showDigitWithLocation(11,False,5)
            else:
                showDigitWithLocation(0,False,5)
#-----------------------Multi Treading For Display----------------------
bgThread = threading.Thread(target = displayVoltage, args = ())
bgThread.start()

#---------------------Read Voltage with I2C-----------------------------
def readVoltage():
    global volt
    global movingAverage
    global addaDivisor
    global addaMultiplier
    while True:
        bus.write_byte(address,A0) 
        value = bus.read_byte(address)
        volt1 = round(addaDivisor / addaMultiplier * value, 2)
        movingAverage.append(volt1)
        del movingAverage[0]
        volt = np.average(movingAverage)
        time.sleep(0.3)
		
#-----------------------Multi Treading For ADDA-------------------------
bgThread2 = threading.Thread(target = readVoltage, args = ())
bgThread2.start()

#-----------------------Controlling Reverter Relay----------------------
def switchRelay():
    global solar

    # Allows switching on first run
    # This variable prevents io.output from being called repeatedly
    previousSolar = not solar
    
    while True:
        if solar == True:
            if previousSolar == False:
                if inverterRelayEnabled == True:
                    io.output(inverterRelay, False)
                    time.sleep(3.0)
                io.output(relay,False)
        else:
            if previousSolar == True:
                if inverterRelayEnabled == True:
                    io.output(inverterRelay, True)
                io.output(relay,True)

        previousSolar = solar
            
        time.sleep(0.3)
        
#-----------------------Multi Treading For Relay----------------------
bgThread3 = threading.Thread(target = switchRelay, args = ())
bgThread3.start()

#-----------------------Multi Treading For Fan----------------------
def fan():
    global fanPort

    # close air fan first
    io.setup(fanPort, io.OUT)
    is_close = True
    while True:
        temp = cpu_temp()
        if is_close:
            if temp > 50.0:
                #print time.ctime(), temp, 'open air fan'
                io.output(channel, 1)
                is_close = False
        else:
            if temp < 40.0:
                #print time.ctime(), temp, 'close air fan'
                print('fan close')
                io.output(channel, 0)
                is_close = True

        time.sleep(2.0)
        #print time.ctime(), temp
        print(temp)

if fanEnabled is True:
    bgThread4 = threading.Thread(target = fan, args = ())
    bgThread4.start()

#-----------------------------Main Thread------------------------------

buttonOn = False
solar = False

manualOn = False

while True:
    if city == 0:
        isCity = 5
    else:
        isCity = 10
        
    #---Manual switch
    button = io.input(manualAutoSwitch)
    
    if button == 1 and manualOn == False:
        isManual = not isManual
        manualOn = True
        
    if button == 0:
        manualOn = False
    
    previousManual = manualOn
    
    #---Switching
        
    if isManual == True:
		button = io.input(switchButton)
		
		if button == 1 and buttonOn == False:
			solar = not solar
			buttonOn = True
			
		if button == 0:
			buttonOn = False
			
		if volt < 11.0:
			#Force city power when battery is dead
			on = False	
    else:
		#Auto
		if volt >= 12.6:
			solar = True
			
		if volt <= 11.2:
			solar = False
	
    city = not solar
    
    previousOn = solar

    #LEDs
    if ledEnabled == True:
        io.output(manualModeLED, isManual)
        io.output(solarEnergyLED, solar)
        io.output(gridIndicator, city)
    
    time.sleep(0.1)
