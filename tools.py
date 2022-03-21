import numpy as np
from scipy.spatial.transform import Rotation
from inekf import SE3

class State:
    def __init__(self, state, last_meas_omega=None):
        self.vec = np.zeros(12)
        self.mat = np.eye(5)
        self.bias = np.zeros(6)

        # True State
        if isinstance(state, dict):
            self.vec[0:3] = state["PoseSensor"][:3,3]
            self.vec[3:6] = state["VelocitySensor"]
            self.vec[6:9] = rot_to_rpy(state["PoseSensor"][:3,:3])
            self.vec[9:12] = state["IMUSensorClean"][1]

            self.bias[0:3] = state["IMUSensor"][2]
            self.bias[3:6] = state["IMUSensor"][3]

            self.mat[:3,:3] = state["PoseSensor"][:3,:3]
            self.mat[:3,3] = state["VelocitySensor"]
            self.mat[:3,4] = state["PoseSensor"][:3,3]

        # Estimated State
        if isinstance(state, SE3[2,6]):
            self.vec[0:3] = state[1]
            self.vec[3:6] = state[0]
            self.vec[6:9] = rot_to_rpy(state.State[:3,:3].copy())

            if last_meas_omega is None:
                raise ValueError("Need a measurement for angular velocity")
            self.vec[9:12] = last_meas_omega - state.Aug[:3]

            self.bias = state.Aug
            self.mat = state.State

        # Commanded State
        if isinstance(state, np.ndarray):
            self.vec = state

    @property
    def data_plot(self):
        return np.append(self.vec[:9], self.bias)

def rot_to_rpy(mat):
    return Rotation.from_matrix(mat).as_euler("xyz")*180/np.pi