import numpy as np

from vrep_api import vrep
from vrep_pioneer import VrepPioneer


def main():
    client_id = vrep.simxStart('127.0.0.1', 19996, True, True, 5000, 5)

    pioneers = [VrepPioneer('', client_id), VrepPioneer('#0', client_id)]

    log_sensors = str()

    while pioneers[0].is_connected():

        current_sensors_values = str()
        for pioneer in pioneers:
            sensors = pioneer.get_ultrasonic_sensor_values()
            rounded_sensors_value = np.around(sensors, 3)
            string_sensor_values = ",".join(map(str, rounded_sensors_value))
            if len(current_sensors_values) == 0:
                current_sensors_values = string_sensor_values
            else:
                current_sensors_values += f",{string_sensor_values}"

        log_sensors += f"{current_sensors_values}\n"

    with open('log_pioneers.csv', 'w') as file:
        file.write(log_sensors)


if __name__ == '__main__':
    main()
