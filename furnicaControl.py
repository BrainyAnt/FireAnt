import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

MOTOR11 = 16
MOTOR12 = 18
MOTOR1pwm = GPIO.PWM(12, 50)
MOTOR21 = 29
MOTOR22 = 31
MOTOR2pwm = GPIO.PWM(35, 50)
STANDBY = 38

def init():
    GPIO.setup(STANDBY, GPIO.OUT)
    GPIO.setup(MOTOR11, GPIO.OUT)
    GPIO.setup(MOTOR12, GPIO.OUT)
    GPIO.setup(MOTOR21, GPIO.OUT)
    GPIO.setup(MOTOR22, GPIO.OUT)
    MOTOR1pwm.start(0)
    MOTOR2pwm.start(0)

def getLRspeeds(fwd, left, right, back):
    advance = fwd - back
    steer = right - left
    
    speedLM = (advance + steer)/2
    speedRM = (advance - steer)/2
    
    return (speedLM, speedRM)

def runMotors(fwd, lwft, right, back):

    (speedLM, speedRM) = getLRspeeds(fwd, lwft, right, back)

    if speedLM>=0:
        GPIO.output(MOTOR11, GPIO.HIGH)
        GPIO.output(MOTOR12, GPIO.LOW)
    else:
        GPIO.output(MOTOR11, GPIO.LOW)
        GPIO.output(MOTOR11, GPIO.HIGH)
    MOTOR1pwm.ChangeDutyCycle(abs(speedLM))
    
    if speedRM>=0:
        GPIO.output(MOTOR21, GPIO.HIGH)
        GPIO.output(MOTOR22, GPIO.LOW)
    else:
        GPIO.output(MOTOR21, GPIO.LOW)
        GPIO.output(MOTOR22, GPIO.HIGH)
    MOTOR2pwm.ChangeDutyCycle(abs(speedRM))

def start():
    GPIO.output(STANDBY, GPIO.HIGH)

def stop():
    GPIO.output(STANDBY, GPIO.LOW)

def clear():
    GPIO.cleanup()
