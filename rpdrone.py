import sys
from rpdrone.sensor.mpu import MPUSensor

def main():
    
    mpu_sensor = MPUSensor(smbus_line=1, i2c_addr=0x68, refresh_freq=10)
    
    mpu_sensor.run()

    sys.exit(0)

if __name__ == '__main__':
    main()