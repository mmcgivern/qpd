#start things off

import time
import RPi_GPIO
import RPi.GPIO as GPIO
import datetime
import sys
import os
import smbus
from hx711 import HX711
DEBUG = 1



#LCD init
import Adafruit_CharLCD as LCD
lcd = LCD.Adafruit_CharLCDPlate()
# Make list of button value, text
buttons = ( (LCD.SELECT, 'Select'),
            (LCD.LEFT,   'Left'),
            (LCD.UP,     'Up'),
            (LCD.DOWN,   'Down'),
            (LCD.RIGHT,  'Right') )

lcd.message('loading')
manualmsg = '1/2 up,7/8 down\n# to exit'


#Menu system init
menu_items = ('Manual Adjust', 'Uplift Test', 'Change ID', 'Options')
menu_iter = 0
menu_items_options = ('A', 'B', 'C', 'D', 'Back')
options_iter = 0
menustate = 'main'
dblproc = False

#logging init
userid = 'None'
path = '/quadpod/log files/'
testprepiter = 0
usbpath = '/media/pi/ESD-USB/qpd'
dircon = 0

#Load cell init
mass_unit = 'lbs'
#digit 1: data. digit 2: clock.
hx = HX711(12,1)
hx.set_reference_unit(102.74)

#TODO: make a func for lbs kg conv

#Keypad init
kp = RPi_GPIO.keypad(columnCount = 3) #pins declared in separate file
def digit():
    # Loop while waiting for a keypress
    r = None
    while r == None:
        r = kp.getKey()
    return r

def numeral(): #copy of digit() except that it will never return # / * chars.
    r = None   #used for filenames, etc
    while r == None:
        r = kp.getKey()
        if r in ['*','#']:
            r = None
    return r    
    

#motor controller init
bus = smbus.SMBus(1)  # the chip is on bus 1 of the available I2C buses
addr = 0x40           # I2C address of the PWM chip.#nothing yet
basespeed = 1300
slowspeed = 30
medspeed = 150
fastspeed = 400
bus.write_byte_data(addr, 0, 0x20)     # enable the chip
bus.write_byte_data(addr, 0xfe, 0x1e)  # configure the chip for multi-byte write

bus.write_word_data(addr, 0x06, 0)     # chl 0 start time = 0us
bus.write_word_data(addr, 0x08, basespeed)  # chl 0 end time = 1.5ms


#Potentiometer init
def RCtime (RCpin): #rcpin is 24 unless listed elsewhere
    reading = 0
    GPIO.setup(RCpin, GPIO.OUT)
    GPIO.output(RCpin, GPIO.LOW)
    time.sleep(0.1)
    
    GPIO.setup(RCpin, GPIO.IN)
    
    while (GPIO.input(RCpin) == GPIO.LOW):
        reading += 1
    return reading

#########################################################################################

lcd.clear() #1234567890123451234567890123456
lcd.message('APEC Quad Pod\n')
os.chdir('/home/pi/testlogs') #changes active directory to where USB drives populate)
dircontents = os.listdir('/media/pi/') 
dircontents.remove('SETTINGS')
##time.sleep(1.5)
##lcd.clear()
##if len(dircontents) == 0:
##    lcd.message('No USB found!\nPlease reset')
##    time.sleep(999)
##elif len(dircontents) == 1:
##    lcd.message('Using dir\n' + dircontents[0])
time.sleep(1)
lcd.clear()
lcd.message('# to select\n* to navigate')
menustate = 'main'
##else:
##    menustate = 'excess'    

#######################################################################################

while True:
    while menustate == 'excess':
        lcd.message('2+ USBs detected\nSelect log drive')
        time.sleep(2)
        lcd.clear()
        lcd.message('1.' + str(dircontents[0])[0:9] + '\n2.' + str(dircontents[1])[0:9])
        if str(digit())== '1':
            lcd.clear()
            dircon = 0
            menustate == 'main'
            lcd.message('# to select\n* to navigate')
            time.sleep(0.23)
        if str(digit())== '2':
            lcd.clear()
            dircon = 1
            menustate = 'main'
            lcd.message('# to select\n* to navigate')
            time.sleep(0.23)
    while menustate == 'main':
        if str(digit())== '*':
            menu_iter = menu_iter + 1
            if menu_iter == len(menu_items):
                menu_iter = 0
            lcd.clear()
            lcd.message('Main Menu\n'+ menu_items[menu_iter])
            time.sleep(0.25) 
        if str(digit()) =='#':
            if menu_iter == 0:
                menustate = 'manual'
                lcd.clear()##1234567890123456
                lcd.message(manualmsg)
            elif menu_iter == 1:
                menustate = 'logging1'
            elif menu_iter == 2:
                menustate = 'enterID'
            elif menu_iter == 3:
                menustate = 'options'
                lcd.clear()
                if mass_unit == 'lbs': 
                    lcd.message('Pounds or Kilos?\n^^^^^^')
                if mass_unit == 'kg':
                    lcd.message('Pounds or Kilos?\n          ^^^^^^')
            time.sleep(0.25)
    while menustate == 'manual':
        if str(digit()) == '1':
            print('going up')
            bus.write_word_data(addr, 0x08, basespeed - fastspeed)  # chl 0 end time = 1.0ms
            time.sleep(2)
            bus.write_word_data(addr, 0x08, basespeed)  # chl 0 end time = 2.0ms 
        elif str(digit()) == '7':
            print('going down')
            bus.write_word_data(addr, 0x08, basespeed + fastspeed)  # chl 0 end time = 1.0ms
            time.sleep(2)
            bus.write_word_data(addr, 0x08, basespeed)  # chl 0 end time = 2.0ms
        elif str(digit()) == '2':
            print('going up medium')
            bus.write_word_data(addr, 0x08, basespeed - medspeed)  # chl 0 end time = 1.0ms
            time.sleep(2)
            bus.write_word_data(addr, 0x08, basespeed)  # chl 0 end time = 2.0ms
        elif str(digit()) == '8':
            print('going down medium')
            bus.write_word_data(addr, 0x08, basespeed + medspeed)  # chl 0 end time = 1.0ms
            time.sleep(2)
            bus.write_word_data(addr, 0x08, basespeed)  # chl 0 end time = 2.0ms 
        elif str(digit()) == '#':
            menustate = 'main'
            lcd.clear()
            lcd.message('Main Menu\n'+ menu_items[menu_iter])
        time.sleep(0.25)
    while menustate == 'logging1':
        lcd.clear()
        if userid == 'None':
            menustate = 'enterID'
        else:#######################################1234567890123456
            lcd.message('ID is ' + str(userid) + '\nEnter bldng num.')
            bldg = '***'
            bg1 = str(numeral())
            bldg = bg1 + '**'
            lcd.clear()
            lcd.message('Building no:\n  ' + str(bldg))
            time.sleep(0.25)
            bg2 = str(numeral())
            bldg = bg1 + bg2 + '*'
            lcd.clear()
            lcd.message('Building no:\n  ' + str(bldg))
            time.sleep(0.25)
            bg3 = str(numeral())
            bldg = bg1 + bg2 + bg3
            lcd.clear()
            tstno = '***'
            lcd.message('Bldg no:' + str(bldg) + '\nEnter test num.')
            time.sleep(1.25)
            ts1 = str(numeral())
            tstno = ts1 + '**'
            lcd.clear()
            lcd.message('Building no:\n  ' + str(tstno))
            time.sleep(0.25)
            ts2 = str(numeral())
            tstno = ts1 + ts2 + '*' 
            lcd.clear()
            lcd.message('Building no:\n  ' + str(tstno))
            time.sleep(0.25)
            ts3 = str(numeral())
            tstno = ts1 + ts2 + ts3
            lcd.clear()
            lcd.message('Bldg no:' + str(bldg) + '\nTest no:' + str(tstno))
##        else: #please clean this up eventually
##            lcd.message('ID is ' + str(userid) + '\nEnter test num.')
##            filename = '******'
##            fn1 = str(numeral())
##            filename = fn1 + '*****'
##            lcd.clear()
##            lcd.message('Filename\n  ' + str(filename))
##            time.sleep(0.25)
##            fn2 = str(numeral())
##            filename = fn1 + fn2 + '****'
##            lcd.clear()
##            lcd.message('Filename\n  ' + str(filename))
##            time.sleep(0.25)
##            fn3 = str(numeral())
##            filename = fn1 + fn2 + fn3 + '***'
##            lcd.clear()
##            lcd.message('Filename\n  ' + str(filename))
##            time.sleep(0.25)
##            fn4 = str(numeral())
##            filename = fn1 + fn2 + fn3 + fn4 + '**'
##            lcd.clear()
##            lcd.message('Filename\n  ' + str(filename))
##            time.sleep(0.25)
##            fn5 = str(numeral())
##            filename = fn1 + fn2 + fn3 + fn4 + fn5 + '*'
##            lcd.clear()
##            lcd.message('Filename\n  ' + str(filename))
##            time.sleep(0.25)
##            fn6 = str(numeral())
##            filename = fn1 + fn2 + fn3 + fn4 + fn5 + fn6
##            lcd.clear()
##            lcd.message('Your test # is\n  ' + str(filename))
            time.sleep(1)
            if str(digit())== '#':
                lcd.clear()
                lcd.message('Creating file...')
                hx.reset()
                hx.tare()
                logfile = open(bldg + '_' + tstno + '_' + str(datetime.datetime.now())[18:19] + '.csv', 'w+')
                print('file opened')
                logfile.write('User,' + userid + '\nBuilding,' + bldg + '\nTest number,' + tstno + '\nStart time,' + str(datetime.datetime.now())[11:19] + '\nStart date,' + str(datetime.datetime.now())[0:10] +'\nMass units,' + mass_unit)
                logfile.write('\nTick,Distance,Load\n')
                lcd.message('\nDone.')
                time.sleep(1.0)
                menustate = 'testprep'
                lcd.clear()
                lcd.message('Press # to\nload to 10lb')
            
    while menustate == 'testprep':
        time.sleep(0.1)
        val = 0
            #not actual procedure! waiting on LA. currently counts to 60 on the disp then moves to next state
        if str(digit()) == '#':
            bus.write_word_data(addr, 0x08, 1265)
            while abs(round(val,4)) < 1000:
                lcd.clear()
                val = hx.get_weight(5)
                print round(val,4)
                hx.power_down()
                hx.power_up()
                #logfile.write(str(testprepiter) + "," + str(RCtime(24))+',' + str(round(val,4))+'\n')
                #testprepiter = testprepiter + 1
                #print(RCtime(21))
            bus.write_word_data(addr, 0x08, 1300)
            lcd.message("Loaded at\n" + str(round(val,4) / 100))
            print('succ')
            time.sleep(1.3)
            digit()
            lcd.clear()
            lcd.message("Press # to\ntest sample")
            if str(digit()) == '#':
                menustate ='testing'
                testprepiter = 0
        
            
    while menustate == 'testing':
        print('test active!')
        lcd.clear()
        lcd.message('Test commencing...\nPress 0 to end')
        time.sleep(1)
        load = 0
        testiter = 0
        maxload = -400
        bus.write_word_data(addr, 0x08, 1265)
        GPIO.setup(19, GPIO.OUT)
        GPIO.output(19, GPIO.LOW)

        GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        tmpRead = 1
        testactive = True

        while testactive == True:
            val = hx.get_weight(5)
            hx.power_down()
            hx.power_up()
            #logfile.write(str(testprepiter) + "," + str(RCtime(21))+',' + str(round(val,4))+'\n')
            logfile.write(str(testprepiter) + "," + str(1)+',' + str(round(val,4))+'\n')
            testprepiter = testprepiter + 1
            if abs(val)> maxload:
                maxload = abs(val)
            print('currentload ' + str(round(val,4)))
            print('max load in test' + str(maxload))
            testiter = testiter + 1
            print(str(testiter) + 'test iter') 
            if testiter % 5 == 0:
                lcd.clear()
                lcd.message('Max Load:' + str(maxload) + '\nLoad: ' +  str(round(val,4)))
            tmpRead = GPIO.input(16)
            if str(tmpRead) == "0":
                testactive = False
            print(tmpRead, testactive)
            #some sort of one tenth of second delay to ensure motor still runs
            #but gives delay in log
            #every 10 points, display load and travel
            
            #end test condition: 30% drop in load. stack 6 values, median top and bottom 3,
            #then end test if 30% drop?
            #then testactive == False
        bus.write_word_data(addr, 0x08, 1300)
        menustate = 'posttest'
    while menustate == 'posttest':
        lcd.clear()
        lcd.message('Test complete.\nMax load: '+ str(maxload / 100))
        time.sleep(5)
        digit()
        lcd.clear()
##        lcd.message('Max travel:' + str(maxtravel)) #get from reading file at the end?
##        time.sleep(2)
##        digit()
##        lcd.clear()
        lcd.message('Press #: menu\nMax:' + str(maxload / 100))
        time.sleep(2)
        if digit() == '#':
            menustate = 'manual'
            lcd.clear()##1234567890123456
            lcd.message(manualmsg)
            time.sleep(1)
    while menustate == 'enterID':
        lcd.clear()
        lcd.message('Enter 3 digit\nID code now')
        id1 = numeral()
        lcd.clear()
        lcd.message('User ID\n  ' + str(id1) + '**')
        time.sleep(0.5)
        id2 = numeral()
        lcd.clear()
        lcd.message('User ID\n  ' + str(id1) + str(id2) + '*')
        time.sleep(0.5)
        id3 = numeral()
        userid = str(id1) + str(id2) + str(id3)
        lcd.clear()
        lcd.message('ID is ' + userid )
        time.sleep(2)
        menustate = 'main'
        if userid == '007':
            lcd.clear()
            lcd.message('Good Morning,\nAgent Bond.')
            time.sleep(2)
        lcd.clear()
        lcd.message('Main Menu\n'+ menu_items[menu_iter])
    while menustate == 'options':

#        if lcd.is_pressed(LCD.RIGHT):
#            options_iter = options_iter + 1
#            if options_iter == len(menu_items_options):
#                options_iter = 0
#            lcd.clear()
#            lcd.message('Options\n'+ menu_items_options[options_iter])
#            time.sleep(0.25)
#        if lcd.is_pressed(LCD.LEFT):
#            options_iter = options_iter - 1
#            lcd.clear()
#            lcd.message('Options\n'+ menu_items_options[options_iter])
#            print(options_iter)
#            time.sleep(0.25)
#            if options_iter == -1:
#                options_iter = 4
        if str(digit())== '*':
            if mass_unit == 'kg':
                mass_unit = 'lbs'
                lcd.clear()
                lcd.message('Pounds or Kilos?\n^^^^^^')
                time.sleep(0.25)
                print('lbs')
                dblproc = True
            if mass_unit == 'lbs' and dblproc != True:
                mass_unit = 'kg'
                lcd.clear()
                lcd.message('Pounds or Kilos?\n          ^^^^^^')
                time.sleep(0.25)
                print('kgs')
            dblproc = False
        if str(digit()) =='#':
            options_iter = 0
            menu_iter = 0
            menustate = 'main'
            lcd.clear()
            lcd.message('Main Menu\n'+ menu_items[menu_iter])
            time.sleep(0.25)
#            if options_iter == 4:
#                options_iter = 0
#                menu_iter = 0 
#                lcd.clear()
#                lcd.message('Main Menu\n'+ menu_items[menu_iter])
#                menustate = 'main'
#                time.sleep(0.5)
##while True:
    # Loop through each button and check if it is pressed.
  #  for button in buttons:
   #     if lcd.is_pressed(button[0]):
    #        # Button is pressed, change the message and backlight.
     #       lcd.clear()
      #      lcd.message(button[1])