import numpy as np
import csv
import pickle
import time
from pathlib import Path


# Calibration method (one time, per sensor, depends on accuracy):
# 1. Check dx0, dy0 for both sensors when device is static
# 2. Check dx-scale when device moving with constant x velocity
# 3. Check dy-scale when device moving with constant y velocity
# 4. Compute frame transformation (alpha angle) from data in step 2
# 5. Compute transformed dx0 and dy0 by transforming step 1 results
# 6. Compute transformed x,y scale by transforming step 2+3 results

# What the code does
# With calibration data:
# - Calculate 2x2 transformation matrix for each sensor that rotates xy to FT frame
# - Calculate x- and y-bias for each sensor
# With measurement data:
# - Unpack and structure measurement data from CSV
# - Subtract possible bias from each sensor
# - Scale measurements from each sensor
# - Transform each sensor's data to aligned frame
# - Calculate FT frame's x and y velocity and angular velocity around z
# - Structure and output FT frame's velocities, attached to timestamp


class CalibrationConfig:
    def __init__(self, calibDataPaths: tuple, vRefs: tuple):
        vRefX, vRefY = vRefs
        self.alpha = 0
        self.alphaVar = 0
        self.bias = np.zeros(shape=(2,1))  # for original frame
        self.scale = np.ones(shape=(2,1))  # for original frame
        self.frame = np.eye(2)

        self._unpack_data(calibDataPaths)
        self._calculate_bias(self.staticData)
        self._calculate_scale(self.constVelXData, vRefX, 0)
        self._calculate_scale(self.constVelYData, vRefY, 1)
        self._calculate_transformation(self.constVelXData)

    def _unpack_data(self, rawCalibData):
        # Unpacks tuple of strings (file paths) and reads csv into np array
        staticPath, constVelXPath, constVelYPath = rawCalibData
        self.staticData = np.genfromtxt(staticPath, delimiter=",", skip_header=1)
        self.constVelXData = np.genfromtxt(constVelXPath, delimiter=",", skip_header=1)
        self.constVelYData = np.genfromtxt(constVelYPath, delimiter=",", skip_header=1)
        if np.isnan(self.staticData).any():
            ValueError("Static data contains NaN values")
        if np.isnan(self.constVelXData).any():
            ValueError("Const vel X data contains NaN values")
        if np.isnan(self.constVelYData).any():
            ValueError("Const vel Y data contains NaN values")
            
    def _calculate_bias(self, staticData: dict):
        self.bias[0] = np.mean(staticData[:,0], axis=0)
        self.bias[1] = np.mean(staticData[:,1], axis=0)
        if self.bias.shape != (2,1):
            IndexError("Dimensions of bias not correct")

    def _calculate_scale(self, constVelData: dict, vRef: float, axis: int):
        vConstMean = np.transpose(np.mean(constVelData[:,axis], axis=0))
        self.scale[axis] = vRef / vConstMean
        if self.scale.shape != (2,1):
            IndexError("Dimensions of scale not correct")

    def _calculate_transformation(self, constVelXData):
        alpha = np.arctan2(constVelXData[:,1], constVelXData[:,0])
        self.alpha = np.mean(alpha)  # let alpha be mean of measurements
        self.alphaVar = np.var(alpha)  # save variance of alpha for analysis
        self.frame = np.array([[np.cos(self.alpha), np.sin(self.alpha)],
                              [-np.sin(self.alpha), np.cos(self.alpha)]])
        if self.frame.shape != (2,2):
            IndexError("Dimensions of transformation not correct")

    def save_to_file(self, filename: str):
        filepath = Path(".") / "CalibConfigs" / filename
        print(filepath)
        with filepath.open('wb') as file:
            pickle.dump(self, file)

    def unpack(self):
        return self.bias, self.scale, self.frame


class OpticalSensorReading:
    def __init__(self, rawDataPath: dict, calibDataPaths=None, vRefs=None, calibConfigs=None, d=5):
        self.d = d
        if calibDataPaths is not None:
            self._calibrate_sensors(calibDataPaths, vRefs)
            self._save_calib_config()
        else:
            self._read_config(calibConfigs)
        self.rawDataPath = rawDataPath
        self.transformedData = None

        self._read_data()
        self._transform_readings()

    def _calibrate_sensors(self, calibDataPaths, vRefs):
       # calibDataL, calibDataR = calibDataPaths
        self.calibConfigL = CalibrationConfig(calibDataPaths, vRefs)
        self.calibConfigR = CalibrationConfig(calibDataPaths, vRefs)

    def _save_calib_config(self, filename='calibConfig'):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.calibConfigL.save_to_file(filename + '_L_' + timestr + '.pkl')
        self.calibConfigR.save_to_file(filename + '_R_' + timestr + '.pkl')

    def _read_config(self, calibConfigs: tuple):
        # Read config files from tuple of path names
        calibConfigL, calibConfigR = calibConfigs
        with open(calibConfigL, 'rb') as file:
            self.calibConfigL = pickle.load(file)
        with open(calibConfigR, 'rb') as file:
            self.calibConfigR = pickle.load(file)

    def _read_data(self):
        # Turn raw CSV into np-array
        self.rawData = np.genfromtxt(self.rawDataPath, delimiter=",", skip_header=1)
        if np.isnan(self.rawData).any():
            ValueError("Raw data contains NaN values")

    def _transform_readings(self):
        # Let data have columns t/dxL/dyL/dxR/dyR/...
        data = self.rawData
        bData = np.zeros(shape=(data.shape[0], 5))
        biasL, scaleL, frameL = self.calibConfigL.unpack()
        biasR, scaleR, frameR = self.calibConfigR.unpack()
        for row in range(data.shape[0]):
            t = data[row,0]
            if row == 0:
                dt = 1000000.00
            else:
                dt = data[row,0] - data[row-1,0]
            bData[row,0] = t
            bData[row,1] = dt
            vL = scaleL * (np.transpose(data[row,1:2]) - biasL) / dt
            vL = frameL @ vL
            vR = scaleR * (np.transpose(data[row,3:4]) - biasR) / dt
            vR = frameR @ vR
            vMean = np.mean(np.concatenate((vL,vR),axis=1),axis=1)
            bData[row,2] = vMean[0]
            bData[row,3] = vMean[1]
            bData[row,4] = (vL[1] - vR[1]) / (2 * self.d)
        self.transformedData = bData

    def getData(self):
        if self.transformedData is None:
            ValueError("Was not able to transform readings.")
        return self.transformedData
    
