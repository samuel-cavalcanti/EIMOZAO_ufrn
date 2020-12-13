import numpy as np

from pioneer_robot.vrep_api import vrep
from pioneer_robot.vrep_pioneer import VrepPioneer
from slave_modbus import SlaveModBus


def pioneer_status(sensors: np.ndarray):
    red = 8
    yellow = 14
    green = 5

    min_sensor_value = np.min(sensors)

    if min_sensor_value > 0.5:
        return green
    elif min_sensor_value > 0.25:
        return yellow
    return red


def run_pioneer(coil: list, pioneer: VrepPioneer):
    if coil[0]:
        pioneer.run()
    else:
        pioneer.set_velocity_motor(0.0, 0.0)


def send_pioneers_data_to_scada_lts(slave: SlaveModBus, status_pioneers: list, all_sensors: list):
    slave.write_multiple_registers(0, status_pioneers)
    slave.write_multiple_floats(4, all_sensors)


def main():
    client_id = vrep.simxStart('127.0.0.1', 19996, True, True, 5000, 5)
    pioneers = [VrepPioneer(pioneer_tag='', client_id=client_id), VrepPioneer(pioneer_tag='#0', client_id=client_id)]

    with SlaveModBus.build_client_from_json('server_info.json') as slave:
        slave.unit_id(3)
        slave.write_multiple_coils(0, [True, True])

        while pioneers[0].is_connected():
            try:

                first_pioneer_sensors = pioneers[0].get_ultrasonic_sensor_values()
                second_pioneer_sensors = pioneers[1].get_ultrasonic_sensor_values()

                first_pioneer_status = pioneer_status(first_pioneer_sensors)
                second_pioneer_status = pioneer_status(second_pioneer_sensors)

                send_pioneers_data_to_scada_lts(slave, [first_pioneer_status, second_pioneer_status],
                                                first_pioneer_sensors.tolist() + second_pioneer_sensors.tolist())

                run_pioneer(slave.read_coils(0), pioneers[0])
                run_pioneer(slave.read_coils(1), pioneers[1])


            except Exception as e:
                print(e)

        slave.write_multiple_coils(0, [False, False])
        send_pioneers_data_to_scada_lts(slave, [0, 0], np.ones(16 * 2).tolist())


if __name__ == '__main__':
    main()
