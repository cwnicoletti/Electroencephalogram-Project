import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)


while True:
    GPIO.output(2, 1)
    print("LED on!")
    time.sleep(1)
    GPIO.output(2, 0)
    print("LED off!")
    time.sleep(1)
