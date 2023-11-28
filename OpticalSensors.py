import numpy as np
import pickle
import datetime


# Calibration method (one time, per sensor):
# Check dx0, dy0 when device is static
# Check dx-scale when device moving with constant x velocity
# Check dy-scale when device moving with constant y velocity
# Compute frame transformation (alpha angle) from constant velocity test
# Compute dx0 and dy0 by transforming static reading

# What should the code do?
# Calibrate the sensors' xy-coordinate systems to coordinate system of FT sensor
# Only once, when mounted to the frame
# Calculate 2x2 transformation matrix for each sensor that rotates xy to FT frame
# Calibrate sensors' output wrt bias/drift (only once or every time?)
# Perform controlled action and compare readings to determine dx0, dy0
# Input: dx+dy for both sensors in real time, attached to timestamp
# Transform to aligned frame
# Calculate FT frame's x and y velocity and angular velocity around z
# Output: FT frame dx, dy and omegaz attached to timestamp


class CalibrationConfig:
    def __init__(self, rawCalibData):
        self.alpha = 0
        self.alphaVar = 0
        self.frame = np.array([[1, 0][0, 1]])
        self.bias = np.array([0][0])  # for new frame
        self.scale = np.array([[1][1]])  # for new frame

        staticData, constVelXData, constVelYData = rawCalibData
        self._calculate_transformation(constVelXData)
        self._calculate_bias(staticData)
        self._calculate_scale(constVelXData, 0)
        self._calculate_scale(constVelYData, 1)

    def _calculate_transformation(self, constVelXData):
        alpha = np.zeros(shape=(1, len(constVelXData.values())))
        for i, v in enumerate(constVelXData.values()):
            alpha[i] = np.arctan2(v[1], v[0])
        self.alpha = np.mean(alpha)  # let alpha be mean of measurements
        self.alphaVar = np.var(alpha)  # save variance of alpha for analysis
        self.frame = np.array([np.cos(self.alpha), np.sin(self.alpha)],
                              [np.sin(self.alpha), -np.cos(self.alpha)])

    def _calculate_bias(self, staticData: dict):
        v0 = np.zeros(shape=(2, len(staticData.values())))
        for i, v in enumerate(staticData.values()):
            v0[0][i] = v[0]
            v0[1][i] = v[1]
        v0mean = np.mean(v0, axis=1)
        self.bias = self.frame @ v0mean

    def _calculate_scale(self, constVelData: dict, vRef: float, axis: int):
        vConst = np.zeros(shape=(2, len(constVelData.values())))
        for i, v in enumerate(constVelData.values()):
            vConst[0][i] = v[0]
            vConst[1][i] = v[1]
        vConstMean = np.mean(vConst, axis=1)
        vConstTransformed = self.frame @ vConstMean
        self.scale[axis] = vRef / vConstTransformed[axis]

    def save_to_file(self, filename: str):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    def unpack(self):
        return self.frame, self.bias, self.scale


class OpticalSensorReading:
    def __init__(self, rawData: dict, calibData=None, calibConfigs=None):
        self.d = 5
        if calibData is not None:
            self._calibrate_sensors(calibData)
            self._save_calib_config()
        else:
            self._read_config(calibConfigs)
        self.rawData = rawData
        self._transform_readings()

    def _calibrate_sensors(self, calibData):
        calibDataL, calibDataR = calibData
        self.calibConfigL = CalibrationConfig(calibDataL)
        self.calibConfigR = CalibrationConfig(calibDataR)

    def _save_calib_config(self, filename='calibConfig'):
        time = str(datetime.datetime.now())
        self.calibConfigL.save_to_file(filename + '_L_' + time)
        self.calibConfigL.save_to_file(filename + '_R_' + time)

    def _read_config(self, calibConfigs):
        calibConfigL, calibConfigR = calibConfigs
        with open(calibConfigL, 'rb') as file:
            self.calibConfigL = pickle.load(file)
        with open(calibConfigR, 'rb') as file:
            self.calibConfigR = pickle.load(file)

    def _read_data(self):
        # Turn raw CSV into np-array
        self.rawDataArray = np.array(self.rawData)

    def _transform_readings(self):
        # Let data have columns t/dxL/dyL/dxR/dyR/...
        data = self.rawDataArray
        bData = np.zeros(shape=(len(data, 0), 5))
        frameL, biasL, scaleL = self.calibConfigL.unpack()
        frameR, biasR, scaleR = self.calibConfigR.unpack()
        for row in range(len(data, 0)):
            t = data[row][0]
            if row == 0:
                dt = np.inf
            else:
                dt = data[row][0] - data[row - 1][0]
            bData[row][2:3] = [t, dt]
            vL = (data[row][1:2] + biasL) / dt  # bias in wrong frame
            vL = frameL @ np.transpose(vL)
            vL = vL
            vR = (data[row][3:4] + biasR) / dt
            bData[row][2:3] = np.mean([vL, vR])
            bData[row][4] = (vL[1] - vR[1]) / (2 * self.d)
        self.transformedData = bData


def unpack_data(OptSensData):
    dx = np.array([])
    dy = np.array([])
    return dx, dy


def structure_data(dx, dy, dOmegaz):
    data = [dx, dy, dOmegaz]
    return data


def get_naive_base_velocities(OptSensL, OptSensR, d):
    # Assumes base frame inbetween sensor L and R (on x-axes) with distance d to each.
    dxL, dyL = unpack_data(OptSensL)
    dxR, dyR = unpack_data(OptSensR)
    dxB = np.mean(dxL, dxR, axis=1)
    dyB = np.mean(dyL, dyR, axis=1)
    dOmegazB = (dyL - dyR) / (2 * d)
    baseVel = structure_data(dxB, dyB, dOmegazB)
    return baseVel
