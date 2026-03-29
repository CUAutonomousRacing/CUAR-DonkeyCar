import time
import board
import busio
import adafruit_icm20x

class ICM20649:
    """
    DonkeyCar part for ICM-20649 IMU
    """
    def __init__(self, poll_delay=0.0166):
        """
        poll_delay: seconds between reads (default ~60Hz)
        """
        # Initialize I2C
        i2c = busio.I2C(board.SCL, board.SDA)
        
        # Initialize the ICM20649
        self.imu = adafruit_icm20x.ICM20649(i2c)
        
        self.poll_delay = poll_delay
        self.on = True
        
        # Initialize sensor values
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 0.0
        self.gyro_x = 0.0
        self.gyro_y = 0.0
        self.gyro_z = 0.0
        
        print("ICM20649 initialized")
        
    def update(self):
        """
        Read current IMU values
        """
        while self.on:
            # Read accelerometer (returns tuple of x, y, z)
            accel = self.imu.acceleration
            self.accel_x = accel[0]
            self.accel_y = accel[1]
            self.accel_z = accel[2]
            
            # Read gyroscope (returns tuple of x, y, z)
            gyro = self.imu.gyro
            self.gyro_x = gyro[0]
            self.gyro_y = gyro[1]
            self.gyro_z = gyro[2]
            
            time.sleep(self.poll_delay)
    
    def run_threaded(self):
        """
        Return current IMU values for DonkeyCar
        """
        return (
            self.accel_x, self.accel_y, self.accel_z,
            self.gyro_x, self.gyro_y, self.gyro_z
        )
    
    def run(self):
        """
        Non-threaded mode - read and return immediately
        """
        accel = self.imu.acceleration
        gyro = self.imu.gyro
        
        return (
            accel[0], accel[1], accel[2],
            gyro[0], gyro[1], gyro[2]
        )
    
    def shutdown(self):
        """
        Cleanup
        """
        self.on = False
        time.sleep(0.1)