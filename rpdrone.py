import sys
import time
from rpdrone.sensor.mpu import MPUSensor
from rpdrone.motors.motors import MotorsController

REFRESH_RATE = 1000
DEGREE_TOLERANT = 4


def autohover():
    print('-- AUTOHOVER --')
    
    try:
        while True:
            try:
                x, y = mpu_sensor.get_rot_data()
            except OSError:
                x, y = mpu_sensor.angle_x, mpu_sensor.angle_y
                
            fr, fl, br, bl = motors_controller.FR_SPEED, motors_controller.FL_SPEED, motors_controller.BR_SPEED, motors_controller.BL_SPEED
            print(f'X: {round(x, 5)}; Y: {round(y, 5)} | FR({fr}), FL({fl}), BR({br}), BL({bl})', end='\r')

            x_steady, y_steady = False, False
            if x < DEGREE_TOLERANT * -1:
                # right -> need to rotate left
                motors_controller.rotate_left()
                
            elif x > DEGREE_TOLERANT:
                # left -> need to rotate right
                motors_controller.rotate_right()

            else:
                x_steady = True
                
            if y < DEGREE_TOLERANT * -1:
                # front -> need to rotate backward
                motors_controller.rotate_backward()
            
            elif y > DEGREE_TOLERANT:
                # back -> need to rotate forward
                motors_controller.rotate_forward()
                
            else:
                y_steady = True
                
            if x_steady and y_steady:
                motors_controller.steady()

            time.sleep(1 / REFRESH_RATE)
        
    except KeyboardInterrupt:
        print('-- STOP --')
        motors_controller.stop()
    

def main():
    global mpu_sensor, motors_controller
    
    print('-- INIT --')
    
    mpu_sensor = MPUSensor(smbus_line=1, i2c_addr=0x68)
    motors_controller = MotorsController(fr_pin=16, fl_pin=12, br_pin=21, bl_pin=20)
    
    motors_controller.set_max_motors_speed(1500)
    motors_controller.set_min_motors_speed(1100)
    motors_controller.set_steady_speed(1180)
    motors_controller.set_acceleration(2)
    
    motors_controller.arm_esc()
    motors_controller.steady()
    
    autohover()

    sys.exit(0)

if __name__ == '__main__':
    main()