import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
FAN_OUT_PIN = 12
GPIO.setup(FAN_OUT_PIN, GPIO.OUT)
GPIO.output(FAN_OUT_PIN, GPIO.LOW)

# PWM-Channel initialisieren
pwm0 = GPIO.PWM(FAN_OUT_PIN, 100)       # Frequenz ab 10 Hz funktioniert ganz gut
pwm0.start(0.0)

# Funktionen definieren
def getCpuTemp(): # ermittelt die CPU-Temperatur und gibt sie als String zurueck
    raw = os.popen("vcgencmd measure_temp").readline()
    cpuTemp = (raw.replace("temp=","").replace("'C\n",""))
    return(cpuTemp)

# Hauptprogramm starten


#Setup:
cpuTemp_null = 55.0 #Bis zu dieser cpuTemperatur 0% PWM
cpuTemp_hudred = 80.0 #Ab dieser cpuTemperatur 100% PWM
MinDuty = 40.0 #Kleinster Dutycycle bei dem der Motor noch sicher laeuft
PWMSpeed = 0.02
#------------------------------------------------------------------------------
#Variable initialisieren
FanON = False 
FanState = False
FanOutput = 0.0
cpuTemp = 0.0
#------------------------------------------------------------------------------
while True:
    #Start Hauptprogramm
    cpuTemp = float(getCpuTemp())
    
    #PWM berechnen wenn Temperatur im angegebenen Bereich
    FanOutput = (cpuTemp - cpuTemp_null) * ((100.0-MinDuty) / (cpuTemp_hudred - cpuTemp_null)) + MinDuty #Formel
    
    if FanOutput < MinDuty:
        FanOutput = MinDuty
        
    if FanOutput > 100:
        FanOutput = 100
#---------------------------------------------------------------------------------------
    if (cpuTemp > cpuTemp_null):
        FanState = True # Luefter soll EIN sein
    elif (cpuTemp < cpuTemp_null):
        FanState = False # Luefter soll AUS sein
 #---------------------------------------------------------------------------------------
    #Luefter hochfahren wenn Luefter ein sein soll aber aus ist
    if (FanON == False) and (FanState == True):
        for i in range(101):
            pwm0.ChangeDutyCycle(i)
            time.sleep(PWMSpeed)

        time.sleep(1) #1s auf 100%
        
        Target1 = int (FanOutput) #Von float zu int casten
        for i in range(100,Target1,-1):
            pwm0.ChangeDutyCycle(i)
            time.sleep(PWMSpeed)
        FanON = True #Luefter nun auf Vorgabe
        time.sleep(20) #20s warten um pumpen zu verhindern
#---------------------------------------------------------------------------------------
    #Luefter ausschalten
    if (FanON == True) and (FanState == False):
        pwm0.ChangeDutyCycle(MinDuty)
        time.sleep(60) #Nachlauf
        Target2 = int (MinDuty) #Von float zu int casten
        for i in range(Target2,0,-1):
            pwm0.ChangeDutyCycle(i)
            time.sleep(PWMSpeed)
            FanOutput = 0.0
        pwm0.ChangeDutyCycle(FanOutput)
        FanON = 0 #Luefter ist jetzt AUS
#---------------------------------------------------------------------------------------      
    #Notbremse:
    if cpuTemp >= 90.0:
        os.system("sudo shutdown now")  #Pi herunterfahren
#---------------------------------------------------------------------------------------        
    if FanON == True:    
        pwm0.ChangeDutyCycle(FanOutput)
#---------------------------------------------------------------------------------------  
    time.sleep(10) # 10Sekunden Pause vor dem naechsten Durchlauf
    #Ende Hauptprogramm            
pwm0.ChangeDutyCycle(0)
pwm0.stop()