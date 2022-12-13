import sys
import time
import math
import smbus


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
    
    def __init__(self, smbus_line : int, i2c_addr : int, refresh_freq : int) -> None:
        # Refresh frequency `Hz`
        self.refresh_freq = refresh_freq
        
        # I2C device address
        self.i2c_addr = i2c_addr
        
        # Activate communication via SMBus
        self.bus = smbus.SMBus(smbus_line)
        
        # Activate MPU sensor
        self.bus.write_byte_data(self.i2c_addr, MPUSensor.POWER_MGMT_1, 0)
        
    
    def run(self):
        while True:
            sys.stdout.write("  Gyroscope\n")
            sys.stdout.write("-------------\n")
            gyro_xout = self._read_word_2c(MPUSensor.GYRO_XOUT_ADDR)
            gyro_yout = self._read_word_2c(MPUSensor.GYRO_YOUT_ADDR)
            gyro_zout = self._read_word_2c(MPUSensor.GYRO_ZOUT_ADDR)
            gyro_xout_scaled = gyro_xout / MPUSensor.GYRO_DIVIDER
            gyro_yout_scaled = gyro_yout / MPUSensor.GYRO_DIVIDER
            gyro_zout_scaled = gyro_zout / MPUSensor.GYRO_DIVIDER
            sys.stdout.write(f"X: {gyro_xout} | Scaled: {gyro_xout_scaled}\n")
            sys.stdout.write(f"Y: {gyro_yout} | Scaled: {gyro_yout_scaled}\n")
            sys.stdout.write(f"Z: {gyro_zout} | Scaled: {gyro_zout_scaled}\n")
            
            
            sys.stdout.write("  Accelerometer\n")
            sys.stdout.write("-----------------\n")
            accel_xout = self._read_word_2c(MPUSensor.ACCEL_XOUT_ADDR)
            accel_yout = self._read_word_2c(MPUSensor.ACCEL_YOUT_ADDR)
            accel_zout = self._read_word_2c(MPUSensor.ACCEL_ZOUT_ADDR)
            accel_xout_scaled = accel_xout / MPUSensor.ACCEL_DIVIDER
            accel_yout_scaled = accel_yout / MPUSensor.ACCEL_DIVIDER
            accel_zout_scaled = accel_zout / MPUSensor.ACCEL_DIVIDER
            sys.stdout.write(f"X: {accel_xout} | Scaled: {accel_xout_scaled}\n")
            sys.stdout.write(f"Y: {accel_yout} | Scaled: {accel_yout_scaled}\n")
            sys.stdout.write(f"Z: {accel_zout} | Scaled: {accel_zout_scaled}\n")
            
            
            sys.stdout.write("  Rotation\n")
            sys.stdout.write("------------\n")
            rot_x = self._get_x_rotation(gyro_xout_scaled, gyro_yout_scaled, gyro_zout_scaled)
            rot_y = self._get_y_rotation(gyro_xout_scaled, gyro_yout_scaled, gyro_zout_scaled)
            sys.stdout.write(f"x_rotation: {rot_x}\n")
            sys.stdout.write(f"y_rotation: {rot_y}\n")
            
            
            time.sleep(1 / self.refresh_freq)
            
            
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            sys.stdout.write('\033[A')
            
            sys.stdout.flush()
    
        
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