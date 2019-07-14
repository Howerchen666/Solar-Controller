# -*- coding:utf-8 -*-
#Developed By Tom & Hower
#---------------------------import modules------------------------------
import RPi.GPIO as io
import time
import smbus
import math
import threading

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
io.setup(4, io.OUT)

#Actual Switch Button
io.setup(5,io.IN)

#Manual/Auto Swith Button
io.setup(16,io.IN)

#inverter Relay
io.setup(26,io.OUT)

#Setup Display
DS = 17   #DIO

SHCP = 22 #SCK

STCP = 27 #RCK

io.setup(DS, io.OUT)
io.setup(STCP, io.OUT)
io.setup(SHCP, io.OUT)

io.output(STCP, False)
io.output(SHCP, False)

#Initialize Variable
city = 0
isCity = 5
volt = 9.56
isManual = False
solar = True

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
	while True:
		bus.write_byte(address,A0) 
		value = bus.read_byte(address)
		volt = round(12.4 / 212 * value, 2)
            
		time.sleep(0.3)
		
#-----------------------Multi Treading For ADDA-------------------------
bgThread2 = threading.Thread(target = readVoltage, args = ())
bgThread2.start()

#-----------------------Controlling Reverter Relay----------------------
def switchRelay():
    global solar
    
    while True:
        if solar == True:
            io.output(26, False)
            time.sleep(3.0)
            io.output(4,False)
        else:
            io.output(26, True)
            io.output(4,True)
            
        time.sleep(0.3)
        
#-----------------------Multi Treading For Relay----------------------
bgThread3 = threading.Thread(target = switchRelay, args = ())
bgThread3.start()

#-----------------------------Main Thread------------------------------

io.setup(5, io.IN) #button
io.setup(4, io.OUT)#relay
buttonOn = False
solar = False

manualOn = False

while True:
    if city == 0:
        isCity = 5
    else:
        isCity = 10
        
    #---Manual switch
    button = io.input(16)
    
    if button == 1 and manualOn == False:
        isManual = not isManual
        manualOn = True
        
    if button == 0:
        manualOn = False
    
    previousManual = manualOn
    
    #---Switching
        
    if isManual == True:
		button = io.input(5)
		
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
		if volt > 12.3:
			solar = True
			
		if volt < 11.0:
			solar = False
	
    city = not solar
    
    previousOn = solar
    
    time.sleep(0.1)
