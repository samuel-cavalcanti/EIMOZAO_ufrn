import json

from pyModbusTCP.server import ModbusServer


def load_serve_config(file_name: str) -> (str, int):
    with open(file_name, 'r') as file:
        config = json.load(file)

        return config['ip'], config['port']


def main():
    ip, port = load_serve_config('server_info.json')
    server = ModbusServer(ip, port)
    print('PAI TA ÔN')
    print(f'IP: {ip} port {port}')

    try:
        server.start()

    except Exception as e:
        print(f'shutdown server with exception: {e}')
        server.stop()
        print('server is offline')


if __name__ == '__main__':
    main()
