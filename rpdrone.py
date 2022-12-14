import sys
import time
from rpdrone.sensor.mpu import MPUSensor
from rpdrone.motors.motors import MotorsController

REFRESH_RATE = 100

def autohover():
    print('-- AUTOHOVER --')
    
    try:
        while True:
            x, y = mpu_sensor.get_rot_data()
            print(f'X: {round(x, 5)} | Y: {round(y, 5)}', end='\r')
            
            time.sleep(REFRESH_RATE)
        
    except KeyboardInterrupt:
        print('-- STOP --')
        # motors_controller.stop()
    

def main():
    global mpu_sensor, motors_controller
    
    print('-- INIT --')
    
    mpu_sensor = MPUSensor(smbus_line=1, i2c_addr=0x68, refresh_freq=100, blackbox_data_size=100000, record_black_box=True)
    motors_controller = MotorsController(fr_pin=16, fl_pin=12, br_pin=21, bl_pin=20)
    
    # motors_controller.set_max_motors_speed(35)
    # motors_controller.set_min_motors_speed(10)
    
    # motors_controller.arm_esc()
    
    autohover()

    sys.exit(0)

if __name__ == '__main__':
    main()