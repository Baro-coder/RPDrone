import sys
import time
import math
import smbus


class MPUSensor:
    # Sensor's activate register
    POWER_MGMT_1 = 0x6b
    
    # Gyroscope registers
    GYRO_XOUT_ADDR = 0x43
    GYRO_YOUT_ADDR = 0x45
    GYRO_ZOUT_ADDR = 0x47
    
    # Accelerometer registers
    ACCEL_XOUT_ADDR = 0x3b
    ACCEL_YOUT_ADDR = 0x3d
    ACCEL_ZOUT_ADDR = 0x3f
    
    
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
            sys.stdout.write("gyro data")
            sys.stdout.write("---------")
            gyro_xout = self._read_word_2c(MPUSensor.GYRO_XOUT_ADDR)
            gyro_yout = self._read_word_2c(MPUSensor.GYRO_YOUT_ADDR)
            gyro_zout = self._read_word_2c(MPUSensor.GYRO_ZOUT_ADDR)
            sys.stdout.write(f"gyro_xout: {gyro_xout} | scaled: {(gyro_xout / 131)}")
            sys.stdout.write(f"gyro_yout: {gyro_yout} | scaled: {(gyro_yout / 131)}")
            sys.stdout.write(f"gyro_zout: {gyro_zout} | scaled: {(gyro_zout / 131)}")
            
            
            sys.stdout.write("accelerometer data")
            sys.stdout.write("------------------")
            accel_xout = self._read_word_2c(MPUSensor.ACCEL_XOUT_ADDR)
            accel_yout = self._read_word_2c(MPUSensor.ACCEL_YOUT_ADDR)
            accel_zout = self._read_word_2c(MPUSensor.ACCEL_ZOUT_ADDR)
            accel_xout_scaled = accel_xout / 16383.0
            accel_yout_scaled = accel_yout / 16383.0
            accel_zout_scaled = accel_zout / 16383.0
            
            sys.stdout.write(f"accel_yout: {accel_xout} | scaled: {accel_xout_scaled}")
            sys.stdout.write(f"accel_yout: {accel_yout} | scaled: {accel_yout_scaled}")
            sys.stdout.write(f"accel_yout: {accel_zout} | scaled: {accel_zout_scaled}")
               
            sys.stdout.write("rotation data")
            sys.stdout.write("------------------")
            x = self._get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
            sys.stdout.write(f"x_rotation: {x}")
            y = self._get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
            sys.stdout.write(f"y_rotation: {y}")
            
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
        radians = math.atan2(x, self.dist(y,z))
        return -math.degrees(radians)

    def _get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x,z))
        return math.degrees(radians)