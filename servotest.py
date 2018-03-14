#!usr/bin/python
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)

pwm = GPIO.PWM(4 ,50)

pwm.start(5)
while True:
    n = float(input("DC: "))
    if n==123:break
    pwm.ChangeDutyCycle(n)
    #time.sleep(0.3)
    #pwm.ChangeDutyCycle(0)
GPIO.cleanup()
time.sleep(999999999999999999999999)


##while True:
##    for i in range(50):
##        time.sleep(0.019)
##        GPIO.output(4, True)
##        time.sleep(0.001)
##        GPIO.output(4, False)
##    for i in range(50):
##        time.sleep(0.018)
##        GPIO.output(4, True)
##        time.sleep(0.002)
##        GPIO.output(4, False)
##    
