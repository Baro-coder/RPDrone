class Filter:
    def __init__(self):
        self.QAngle = 0.001
        self.QBias = 0.025
        self.RMeasure = 0.025
        self.angle = 0.0
        self.bias = 0.0
        self.rate = 0.0
        self.P=[[0.0,0.0],[0.0,0.0]]

    def getAngle(self, newAngle, newRate, dt):
        # Step 1:
        self.rate = newRate - self.bias;    #new_rate is the latest Gyro measurement
        self.angle += dt * self.rate

        # Step 2:
        self.P[0][0] += dt * (dt * self.P[1][1] - self.P[0][1] - self.P[1][0] + self.QAngle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.QBias * dt

        # Step 3: Innovation
        y = newAngle - self.angle

        # Step 4: Innovation covariance
        s = self.P[0][0] + self.RMeasure

        # Step 5: Kalman Gain
        K=[0.0,0.0]
        K[0] = self.P[0][0]/s
        K[1] = self.P[1][0]/s

        # Step 6: Update the Angle
        self.angle += K[0] * y
        self.bias  += K[1] * y
 
        # Step 7: Calculate estimation error covariance - Update the error covariance
        P00Temp = self.P[0][0]
        P01Temp = self.P[0][1]

        self.P[0][0] -= K[0] * P00Temp
        self.P[0][1] -= K[0] * P01Temp
        self.P[1][0] -= K[1] * P00Temp
        self.P[1][1] -= K[1] * P01Temp

        return self.angle