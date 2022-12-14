import time
import pigpio


class MotorsController:
    def __init__(self, fr_pin : int, fl_pin : int, br_pin : int, bl_pin : int):
        self.PWM = pigpio.pi()
        
        self.FR = fr_pin
        self.FL = fl_pin
        self.BR = br_pin
        self.BL = bl_pin
        
        self.acceleration = 10
        
        self.steady_speed = 1100
        self.min_speed = 1000
        self.max_speed = 2000
        
        self.FR_SPEED = self.steady_speed
        self.FL_SPEED = self.steady_speed
        self.BR_SPEED = self.steady_speed
        self.BL_SPEED = self.steady_speed
        
    
    def _update_speed(self):
        self.PWM.set_servo_pulsewidth(self.FR, self.FR_SPEED)
        self.PWM.set_servo_pulsewidth(self.FL, self.FL_SPEED)
        self.PWM.set_servo_pulsewidth(self.BR, self.BR_SPEED)
        self.PWM.set_servo_pulsewidth(self.BL, self.BL_SPEED)
        
    def arm_esc(self):
        print ("Disconnect the battery and press Enter")
        inp = input()  
          
        self.PWM.set_servo_pulsewidth(self.FR, 0)
        self.PWM.set_servo_pulsewidth(self.FL, 0)
        self.PWM.set_servo_pulsewidth(self.BR, 0)
        self.PWM.set_servo_pulsewidth(self.BL, 0)
        
        print ("Connect the battery and press Enter")
        inp = input() 
        
        self.PWM.set_servo_pulsewidth(self.FR, 1000)
        self.PWM.set_servo_pulsewidth(self.FL, 1000)
        self.PWM.set_servo_pulsewidth(self.BR, 1000)
        self.PWM.set_servo_pulsewidth(self.BL, 1000)
        time.sleep(2)
        
        print('ESCs are ready!')
        
    
    def steady(self):
        self.FR_SPEED = self.steady_speed
        self.FL_SPEED = self.steady_speed
        self.BR_SPEED = self.steady_speed
        self.BL_SPEED = self.steady_speed
        self._update_speed()
    
    def stop(self):
        self.FR_SPEED = 0
        self.FL_SPEED = 0
        self.BR_SPEED = 0
        self.BL_SPEED = 0
        self._update_speed()
        
        self.PWM.stop()
        
    
    def rotate_forward(self):
        self.FR_SPEED = max(self.FR_SPEED - self.acceleration, self.min_speed)
        self.FL_SPEED = max(self.FL_SPEED - self.acceleration, self.min_speed)
        self.BR_SPEED = min(self.BR_SPEED + self.acceleration, self.max_speed)
        self.BL_SPEED = min(self.BL_SPEED + self.acceleration, self.max_speed)
        self._update_speed()
        
    def rotate_backward(self):
        self.FR_SPEED = min(self.FR_SPEED + self.acceleration, self.max_speed)
        self.FL_SPEED = min(self.FL_SPEED + self.acceleration, self.max_speed)
        self.BR_SPEED = max(self.BR_SPEED - self.acceleration, self.min_speed)
        self.BL_SPEED = max(self.BL_SPEED - self.acceleration, self.min_speed)
        self._update_speed()
        
    def rotate_left(self):
        self.FR_SPEED = min(self.FR_SPEED + self.acceleration, self.max_speed)
        self.FL_SPEED = max(self.FL_SPEED - self.acceleration, self.min_speed)
        self.BR_SPEED = min(self.BR_SPEED + self.acceleration, self.max_speed)
        self.BL_SPEED = max(self.BL_SPEED - self.acceleration, self.min_speed)
        self._update_speed()
        
    def rotate_right(self):
        self.FR_SPEED = max(self.FR_SPEED - self.acceleration, self.min_speed)
        self.FL_SPEED = min(self.FL_SPEED + self.acceleration, self.max_speed)
        self.BR_SPEED = max(self.BR_SPEED - self.acceleration, self.min_speed)
        self.BL_SPEED = min(self.BL_SPEED + self.acceleration, self.max_speed)
        self._update_speed()
        

    def set_steady_speed(self, steady_speed : float):
        self.steady_speed = steady_speed

    def set_min_motors_speed(self, min_speed : float):
        self.min_speed = min_speed
        
    def set_max_motors_speed(self, max_speed : float):
        self.max_spped = max_speed