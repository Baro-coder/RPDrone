import time
import math
import smbus

from rpdrone.filter import kalman


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
    
    
    def get_rot_data(self) -> tuple:
        gyro_data = self.get_gyro_data()
        
        rot_x = self._get_x_rotation(gyro_data[0], gyro_data[1], gyro_data[2])
        rot_y = self._get_y_rotation(gyro_data[0], gyro_data[1], gyro_data[2])
        
        filtered_rot_x = self.kalman_rot_x.getAngle(self.angle_x, rot_x, self.dt)
        filtered_rot_y = self.kalman_rot_y.getAngle(self.angle_y, rot_y, self.dt)
        
        self.angle_x = filtered_rot_x
        self.angle_y = filtered_rot_y
        
        return (filtered_rot_x, filtered_rot_y)
    
    def get_accel_data(self) -> tuple:
        accel_xout = self._read_word_2c(MPUSensor.ACCEL_XOUT_ADDR)
        accel_yout = self._read_word_2c(MPUSensor.ACCEL_YOUT_ADDR)
        accel_zout = self._read_word_2c(MPUSensor.ACCEL_ZOUT_ADDR)
        accel_xout_scaled = accel_xout / MPUSensor.ACCEL_DIVIDER
        accel_yout_scaled = accel_yout / MPUSensor.ACCEL_DIVIDER
        accel_zout_scaled = accel_zout / MPUSensor.ACCEL_DIVIDER
        
        return (accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    
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

    def _dist(self, a, b):
        return math.sqrt((a*a)+(b*b))


    def _get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self._dist(y,z))
        return -math.degrees(radians)

    def _get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self._dist(x,z))
        return math.degrees(radians)