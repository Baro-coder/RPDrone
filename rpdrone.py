import sys
import time
from rpdrone.sensor.mpu import MPUSensor
from rpdrone.motors.motors import MotorsController

# --------------------------------------------
MIN_WIDTH = 1000
MAX_WIDTH = 2000
ACCELERATION = 2

REFRESH_RATE = 100
DEGREE_TOLERANT = 5

# --------------------------------------------

def test_gyro():
    print('-- Gyroscope Test : START --')
    
    for _ in range(1000):
        try:
            x, y = mpu_sensor.get_rot_data()
        except OSError:
            print('MPU.get_rotation - OSError')
            x, y = mpu_sensor.angle_x, mpu_sensor.angle_y
            
        x, y = round(x, 2), round(y, 2)
        
        print(f'(X: {x}; Y: {y})', end='\r')
        
        time.sleep(1 / REFRESH_RATE)
    
    print('-- Gyroscope Test : DONE --')

def test_throttle():
    print('-- Throttle Test : START --')
    
    min_width = 1050
    max_width = 1200
    step = 5
    snooze = 0.5
    
    vehicle.set_width(min_width)
    vehicle._pwm()
    
    time.sleep(2)
    
    print('Increasing...')
    for width in range(min_width, max_width, step):
        vehicle.increase_throttle(step)
        print(f'    Throttle: {width}', end='\r')
        time.sleep(snooze)
        
    print('Holding at max...')
    time.sleep(5)
    
    print('Decreasing...')
    for width in range(max_width, min_width, step * -1):
        vehicle.decrease_throttle(step)
        print(f'    Throttle: {width}', end='\r')
        time.sleep(snooze)
    
    print('-- Throttle Test : DONE --')

# --------------------------------------------

def autohover():
    print('-- AUTOHOVER --')
    
    vehicle.min_width = 1100
    vehicle.max_width = 1250
    
    while True:
        try:
            x, y = mpu_sensor.get_rot_data()
        except OSError:
            print('MPU.get_rotation - OSError')
            x, y = mpu_sensor.angle_x, mpu_sensor.angle_y
            
        x, y = round(x, 2), round(y, 2)
        fr, fl, br, bl = vehicle.esc_widths

        
        print(f'(X: {x}; Y: {y}) - (FR : {fr}; FL : {fl}; BR : {br}; BL : {bl})', end='\r')
        
        if x < DEGREE_TOLERANT * -1:
            # right -> need to rotate left
            vehicle.rotate_left()
            
        elif x > DEGREE_TOLERANT:
            # left -> need to rotate right
            vehicle.rotate_right()
            
        if y < DEGREE_TOLERANT * -1:
            # front -> need to rotate backward
            vehicle.rotate_backward()
        
        elif y > DEGREE_TOLERANT:
            # back -> need to rotate forward
            vehicle.rotate_forward()
        
        time.sleep(1 / REFRESH_RATE)

# --------------------------------------------

def init():
    global mpu_sensor, vehicle
    
    print('Initializing...')
    
    mpu_sensor = MPUSensor(smbus_line=1, i2c_addr=0x68)
    vehicle = MotorsController(fr_pin=20, fl_pin=7, br_pin=21, bl_pin=12, min_width=MIN_WIDTH, max_width=MAX_WIDTH, acceleration=ACCELERATION)

    print('Components ready.')


def start_prep():
    print('Do you want to calibrate ESCs? (y : n)')
    while True:
        opt = input(' > ')
        if opt == 'y' or opt == 'Y':
            vehicle.calibrate()
            break    
        elif opt == 'n' or opt == 'N':
            input('     Connect battery and press ENTER')
            break
        else:
            print('Type `y`, `Y`, `n` or `N`')

    vehicle.arm()


def main():
    try:
        input('\nPress ENTER to run throttle-test')
        test_throttle()

        input('\nPress ENTER to run gyro_test')
        test_gyro()

        input('\nPress ENTER to run autohover')
        autohover()
    
    except KeyboardInterrupt:
        print('-- Manually interrupted --')
    
    except Exception as e:
        print('-- Unexpected Exception --')
        vehicle.stop()
        raise
    
    finally:
        vehicle.stop()
        sys.exit(0)


if __name__ == '__main__':
    init()
    start_prep()
    main()