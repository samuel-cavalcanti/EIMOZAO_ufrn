import json

from pyModbusTCP import utils as modbus_utils
from pyModbusTCP.client import ModbusClient


class SlaveModBus(ModbusClient):

    def __init__(self, host=None, port=None, unit_id=None, timeout=None,
                 debug=None, auto_open=None, auto_close=None):
        super().__init__(host, port, unit_id, timeout,
                         debug, auto_open, auto_close)
        self.hostname = host
        self.port = port

    def write_float(self, address: int, float_number: float):
        integer_32bits_representation = modbus_utils.encode_ieee(float_number)
        integer_represented_in_list_of_16bits = modbus_utils.long_list_to_word([integer_32bits_representation])
        return self.write_multiple_registers(address, integer_represented_in_list_of_16bits)

    def write_multiple_floats(self, address: int, floats_list: list):
        integer_32bits_representation_list = [modbus_utils.encode_ieee(number) for number in floats_list]
        integers_represented_in_list_of_16bits = modbus_utils.long_list_to_word(integer_32bits_representation_list)
        return self.write_multiple_registers(address, integers_represented_in_list_of_16bits)

    @staticmethod
    def build_client_from_json(file_name: str):
        with open(file_name, 'r') as file:
            config = json.load(file)
            return SlaveModBus(config['ip'], config['port'])

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    client = SlaveModBus.build_client_from_json('server_info.json')

    print(f'ip {client.hostname}  port {client.port}')

    opened_status = client.open()

    if not opened_status:
        print('refused connection')
        exit(1)

    client.write_multiple_floats(0, [0.14, 0.15, 0.16, 0.17, 0.18])

    client.close()


if __name__ == '__main__':
    main()
