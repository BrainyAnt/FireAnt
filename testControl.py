def init():
    print("INIT")


def get_lr_speeds(fwd, back, left, right):
    advance = fwd - back
    steer = right - left
    
    speed_lm = (advance + steer)/2
    speed_rm = (advance - steer)/2
    
    return speed_lm, speed_rm


def run_motors(fwd, left, right, back):
    (speedLM, speedRM) = get_lr_speeds(fwd, left, right, back)
    print("{}, {}".format(speedLM, speedRM))


def start():
    # GPIO.output(STANDBY, GPIO.HIGH)
    print("START")


def stop():
    # GPIO.output(STANDBY, GPIO.LOW)
    print("STOP")


def clear():
    # GPIO.cleanup()
    print("CLEAR")
