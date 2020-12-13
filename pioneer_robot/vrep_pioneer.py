import numpy as np

try:
    from vrep_api import vrep
except ModuleNotFoundError:
    from .vrep_api import vrep


class VrepPioneer:

    def __init__(self, pioneer_tag: str, client_id=-1):
        self.__client_id = client_id
        self.__tag = pioneer_tag
        self.__sensors_id = dict()
        self.__sensor_values = - np.ones(16)
        self.__detect = np.zeros(16)
        self.__left_motor_id = -1
        self.__right_motor_id = -1
        self.__body = -1
        self.__data = list()
        self.name = f"Pioneer_p3dx{pioneer_tag}"
        self.__connect_all_peaces()

    def __connect_all_peaces(self):
        self.__connect_all_sensors()
        self.__left_motor_id = self.__connect_peace(f"Pioneer_p3dx_leftMotor{self.__tag}")
        self.__right_motor_id = self.__connect_peace(f"Pioneer_p3dx_rightMotor{self.__tag}")

    def __connect_all_sensors(self):
        vrep_sensor_name = "Pioneer_p3dx_ultrasonicSensor"

        for i in range(1, 17):
            vrep_sensor_full_name = f"{vrep_sensor_name}{i}{self.__tag}"
            self.__sensors_id[vrep_sensor_full_name] = self.__connect_peace(vrep_sensor_full_name)

    def __connect_peace(self, vrep_name: str) -> int:

        status, piece = vrep.simxGetObjectHandle(self.__client_id, vrep_name, vrep.simx_opmode_blocking)

        if status == vrep.simx_return_ok:
            print("conectado ao " + vrep_name)
            return piece
        else:
            print(vrep_name + " não conectado")
            return status

    def get_ultrasonic_sensor_value(self, sensor_id: int) -> float:

        vrep.simxReadProximitySensor(self.__client_id, sensor_id, vrep.simx_opmode_streaming)

        status, detection_state, values, doh, dsnv = vrep.simxReadProximitySensor(self.__client_id, sensor_id,
                                                                                  vrep.simx_opmode_oneshot)
        while status == vrep.simx_return_novalue_flag and self.is_connected():
            status, detection_state, values, doh, dsnv = vrep.simxReadProximitySensor(self.__client_id, sensor_id,
                                                                                      vrep.simx_opmode_buffer)

        if status == vrep.simx_return_ok:

            if detection_state:
                return values[2]

            else:
                return 1
        else:
            raise Exception('Unable to read sensor')

    def _get_ultrasonic_sensor_values(self):

        for i, sensor_id in enumerate(self.__sensors_id.values()):
            self.__sensor_values[i] = self.get_ultrasonic_sensor_value(sensor_id)

    def get_ultrasonic_sensor_values(self) -> np.ndarray:
        self._get_ultrasonic_sensor_values()
        return self.__sensor_values

    def set_velocity_motor(self, left_motor_velocity: float, right_motor_velocity: float):

        vrep.simxSetJointTargetVelocity(self.__client_id, self.__right_motor_id, right_motor_velocity,
                                        vrep.simx_opmode_streaming)

        vrep.simxSetJointTargetVelocity(self.__client_id, self.__left_motor_id, left_motor_velocity,
                                        vrep.simx_opmode_streaming)

    def is_connected(self) -> bool:
        return vrep.simxGetConnectionId(self.__client_id) != -1

    def run(self):
        self._get_ultrasonic_sensor_values()

        braitenberg_l = [-0.2, -0.4, -0.6, -0.8, -1, -1.2, -1.4, -1.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        braitenberg_r = [-1.6, -1.4, -1.2, -1, -0.8, -0.6, -0.4, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        v0 = 2.0
        max_detection_dist = 0.2
        no_detection_dist = 0.5

        for i, distance in enumerate(self.__sensor_values):
            if distance < no_detection_dist:
                if distance < max_detection_dist:
                    distance = max_detection_dist

                self.__detect[i] = 1 - ((distance - max_detection_dist) / (no_detection_dist - max_detection_dist))
            else:
                self.__detect[i] = 0

        velocity_left = v0
        velocity_right = v0

        for i, detect_value in enumerate(self.__detect):
            velocity_left += braitenberg_l[i] * detect_value
            velocity_right += braitenberg_r[i] * detect_value

        self.set_velocity_motor(velocity_left, velocity_right)
