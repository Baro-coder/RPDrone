import time
import math
from statistics import mean
import smbus

from rpdrone.filter import kalman

FIX_Y = 3


class MPUSensor:
    # Sensor's activate register
    POWER_MGMT_1 = 0x6b
    
    # Gyroscope registers
    GYRO_XOUT_ADDR = 0x3b
    GYRO_YOUT_ADDR = 0x3d
    GYRO_ZOUT_ADDR = 0x3f
    
    # Accelerometer registers
    ACCEL_XOUT_ADDR = 0x43
    ACCEL_YOUT_ADDR = 0x45
    ACCEL_ZOUT_ADDR = 0x47
    
    # Scale Dividers
    GYRO_DIVIDER = 16383.0
    ACCEL_DIVIDER = 131
    
    def __init__(self, smbus_line : int, i2c_addr : int) -> None:
        # I2C device address
        self.i2c_addr = i2c_addr
        
        # Activate communication via SMBus
        self.bus = smbus.SMBus(smbus_line)
        
        # Activate MPU sensor
        self.bus.write_byte_data(self.i2c_addr, MPUSensor.POWER_MGMT_1, 0)
        
        # Kalman filter
        self.dt = 0.5
        self.kalman_rot_x = kalman.Filter()
        self.kalman_rot_y = kalman.Filter()
        
        # Angles init
        self.angle_x = 0
        self.angle_y = 0
        
        # Error vars
        self.dx = 0
        self.dy = 0
    
    
    def calibrate(self):
        print(f'{self.__class__}: Calibrating... ')
        
        input(f'{self.__class__}:   Put vehicle on the stable ground and press ENTER')
        
        print(f'{self.__class__}:   Getting data...')
        x_data = []
        y_data = []
        
        for i in range(10000):
            print(f'{self.__class__}:   {round((i / 10000) * 100, 2)}%', end='\r')
            try:
                x, y = self.get_rot_data()
            except OSError:
                print('*', end='')
                x, y = self.angle_x, self.angle_y
            x_data.append(x)
            y_data.append(y)
        print(f'{self.__class__}:   100%')
        
        print(f'{self.__class__}:   Computing mean error...')
        
        self.dx = mean(x_data)
        self.dy = mean(y_data)
        
        print(f'{self.__class__}:   dx = {self.dx} | dy = {self.dy}')
        
        print(f'{self.__class__}: Calibrating finished.')
    
    
    # Compute, filter and get Rotation data
    def get_rot_data(self) -> tuple:
        gyro_data = self.get_gyro_data()
        
        rot_x = self._get_x_rotation(gyro_data[0], gyro_data[1], gyro_data[2])
        rot_y = self._get_y_rotation(gyro_data[0], gyro_data[1], gyro_data[2])
        
        # filtered_rot_x = self.kalman_rot_x.getAngle(self.angle_x, rot_x, self.dt) - self.dx
        # filtered_rot_y = self.kalman_rot_y.getAngle(self.angle_y, rot_y, self.dt) - self.dy
        
        self.angle_x = rot_x
        self.angle_y = rot_y
        
        return (rot_x, rot_y)
    
    # Get Accelerometer data from MPU
    def get_accel_data(self) -> tuple:
        accel_xout = self._read_word_2c(MPUSensor.ACCEL_XOUT_ADDR)
        accel_yout = self._read_word_2c(MPUSensor.ACCEL_YOUT_ADDR)
        accel_zout = self._read_word_2c(MPUSensor.ACCEL_ZOUT_ADDR)
        accel_xout_scaled = accel_xout / MPUSensor.ACCEL_DIVIDER
        accel_yout_scaled = accel_yout / MPUSensor.ACCEL_DIVIDER
        accel_zout_scaled = accel_zout / MPUSensor.ACCEL_DIVIDER
        
        return (accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    
    # Get Gyroscope data from MPU
    def get_gyro_data(self) -> tuple:
        gyro_xout = self._read_word_2c(MPUSensor.GYRO_XOUT_ADDR)
        gyro_yout = self._read_word_2c(MPUSensor.GYRO_YOUT_ADDR)
        gyro_zout = self._read_word_2c(MPUSensor.GYRO_ZOUT_ADDR)
        gyro_xout_scaled = gyro_xout / MPUSensor.GYRO_DIVIDER
        gyro_yout_scaled = gyro_yout / MPUSensor.GYRO_DIVIDER
        gyro_zout_scaled = gyro_zout / MPUSensor.GYRO_DIVIDER
        
        return (gyro_xout_scaled, gyro_yout_scaled, gyro_zout_scaled)
    
    
    # Read single byte
    def _read_byte(self, adr):
        return self.bus.read_byte_data(self.i2c_addr, adr)

    # Convert two bytes to one 16-bit word
    def _read_word(self, adr):
        high = self.bus.read_byte_data(self.i2c_addr, adr)
        low = self.bus.read_byte_data(self.i2c_addr, adr+1)
        val = (high <<8) + low
        return val

    # Binary to decimal val
    def _read_word_2c(self, adr):
        val = self._read_word(adr)
        if(val >= 0x8000): #
            return -((65535 - val) + 1)
        else:
            return val

    # Distance between `a` and `b`
    def _dist(self, a, b):
        return math.sqrt((a*a)+(b*b))

    # Compute Y Rotation
    def _get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self._dist(y,z))
        return -math.degrees(radians)

    # Compute X Rotation
    def _get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self._dist(x,z))
        return math.degrees(radians)