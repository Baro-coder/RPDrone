import time
import pigpio


class MotorsController:
    def __init__(self, fr_pin : int, fl_pin : int, br_pin : int, bl_pin : int, min_width : int = 1000, max_width : int = 2000, acceleration : int = 5):
        # GPIO connection handler
        self.conn = pigpio.pi()
        
        # ESC pins
        self.esc_pins = [fr_pin, fl_pin, br_pin, bl_pin]
        
        # ESC PWM widths
        # FR FL BR BL
        self.esc_widths = [0, 0, 0, 0]
        
        # Single width change value
        self.acceleration = acceleration
        
        # Max and Min PWM width
        self.min_width = min_width
        self.max_width = max_width
    
    # Send `self.esc_width` PWM to `self.esc_pins`
    def _pwm(self, pin_id : int = -1,  snooze : int = 0):
        if pin_id != -1:
            self.conn.set_servo_pulsewidth(self.esc_pins[pin_id], self.esc_widths[pin_id])
            if snooze:
                time.sleep(snooze)
                
        else:
            for esc, width in zip(self.esc_pins, self.esc_widths):
                self.conn.set_servo_pulsewidth(esc, width)
                
            if snooze:
                time.sleep(snooze)
    
    # Update `self.esc_width` PWM
    def set_width(self, width : int, pin_id : int = -1):
        if pin_id != -1:
            self.esc_widths[pin_id] = width
            
        else:
            for i in range(len(self.esc_widths)):
                self.esc_widths[i] = width
    
    
    # Calibrate ESC to `self.min_width` : `self.max_width`
    def calibrate(self):
        print(f'{self.__class__}: Calibrating... ')
        
        self.set_width(self.max_width)
        self._pwm()
        input(f'{self.__class__}:   Connect battery and press ENTER')
    
        print(f'{self.__class__}:   PWM: max width = {self.max_width}')
        self.set_width(self.max_width)
        self._pwm(snooze=2)
    
        print(f'{self.__class__}:   PWM: min width = {self.min_width}')
        self.set_width(self.min_width)
        self._pwm(snooze=5)
    
        print(f'{self.__class__}: Calibration finished.')
    
    # Arm ESC
    def arm(self):
        print(f'{self.__class__}: Arming... ')

        self.set_width(self.min_width)
        self._pwm(snooze=2)

        print(f'{self.__class__}: Arming finished.')
    
    # Slow down Motors to min throttle and turn of ESC
    def stop(self):
        print(f'{self.__class__}: Slowing... ')
        self.set_width(self.min_width)
        self._pwm(snooze=2)
        
        print(f'{self.__class__}: Failsafe... ')
        self.set_width(0)
        self._pwm(snooze=1)
        
        self.conn.stop()
    
    
    # *** THROTTLE ***
    #   Increase
    def increase_throttle(self, step : int = 0):
        if step:
            for i, width in enumerate(self.esc_widths):
                self.set_width(min(width + step, self.max_width), pin_id=i)
        else:
            for i, width in enumerate(self.esc_widths):
                self.set_width(min(width + self.acceleration, self.max_width), pin_id=i)
            
        self._pwm()
    
    # Decrease
    def decrease_throttle(self, step : int = 0):
        if step:
            for i, width in enumerate(self.esc_widths):
                self.set_width(max(width - step, self.min_width), pin_id=i)
        else:
            for i, width in enumerate(self.esc_widths):
                self.set_width(max(width - self.acceleration, self.min_width), pin_id=i)
            
        self._pwm()
    
    
    # *** ROTATING ***
    #   Speed up back motors | Slow down front motors
    def rotate_forward(self):
        # FR
        self.set_width(max(self.esc_widths[0] - self.acceleration, self.min_width), pin_id=0)
        # FL
        self.set_width(max(self.esc_widths[1] - self.acceleration, self.min_width), pin_id=1)
        # BR
        self.set_width(min(self.esc_widths[2] + self.acceleration, self.max_width), pin_id=2)
        # BL
        self.set_width(min(self.esc_widths[3] + self.acceleration, self.max_width), pin_id=3)
        
        self._pwm()
    
    #   Speed up front motors | Slow down back motors
    def rotate_backward(self):
        # FR
        self.set_width(min(self.esc_widths[0] + self.acceleration, self.max_width), pin_id=0)
        # FL
        self.set_width(min(self.esc_widths[1] + self.acceleration, self.max_width), pin_id=1)
        # BR
        self.set_width(max(self.esc_widths[2] - self.acceleration, self.min_width), pin_id=2)
        # BL
        self.set_width(max(self.esc_widths[3] - self.acceleration, self.min_width), pin_id=3)
        
        self._pwm()
    
    #   Speed up right motors | Slow down left motors
    def rotate_left(self):
        # FR
        self.set_width(min(self.esc_widths[0] + self.acceleration, self.max_width), pin_id=0)
        # FL
        self.set_width(max(self.esc_widths[1] - self.acceleration, self.min_width), pin_id=1)
        # BR
        self.set_width(min(self.esc_widths[2] + self.acceleration, self.max_width), pin_id=2)
        # BL
        self.set_width(max(self.esc_widths[3] - self.acceleration, self.min_width), pin_id=3)
        
        self._pwm()
        
    #   Speed up left motors | Slow down right motors
    def rotate_right(self):
        # FR
        self.set_width(max(self.esc_widths[0] + self.acceleration, self.min_width), pin_id=0)
        # FL
        self.set_width(min(self.esc_widths[1] - self.acceleration, self.max_width), pin_id=1)
        # BR
        self.set_width(max(self.esc_widths[2] + self.acceleration, self.min_width), pin_id=2)
        # BL
        self.set_width(min(self.esc_widths[3] - self.acceleration, self.max_width), pin_id=3)
        
        self._pwm()
