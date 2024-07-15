import socket
import sys
import json


def start_server(req_code):
    # Create a UDP socket for negotiation
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', 0))
    n_port = udp_socket.getsockname()[1]
    print(f"SERVER_PORT={n_port}")
    while True:
        # Receive negotiation request from client
        message, client_address = udp_socket.recvfrom(1024)
        request = message.decode().split()
        if len(request) == 3 and request[0] == 'UPLOAD' and request[1] == req_code:
            # print(client_address, request)
            proto = request[2]
            # Generate a random port for TCP connection
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.bind(('', 0))
            r_port = tcp_socket.getsockname()[1]
            # Send the random port number to the client
            udp_socket.sendto(str(r_port).encode(), client_address)

            # Accept TCP connection from the client
            tcp_socket.listen(1)
            connection_socket, addr = tcp_socket.accept()

            # set connection_socket.recv to be non-blocking
            connection_socket.settimeout(0.01)

            data = b""
            while True:
                try:
                    part = connection_socket.recv(4096)
                    data += part
                except socket.timeout:
                    break

            try:
                trace_data = json.loads(data)
            except (json.JSONDecodeError):
                connection_socket.send("Invalid JSON file".encode())
                connection_socket.close()
                tcp_socket.close()
                continue

            # Count packets based on the specified protocol
            counts = count_packets(trace_data, proto)
            connection_socket.send(counts.encode())
            connection_socket.close()
            tcp_socket.close()
        else:
            udp_socket.sendto(b"0", client_address)


def count_packets(data, proto):
    tcp_count = 0
    udp_count = 0
    for packet in data:
        protocols = packet['_source']['layers']['frame']['frame.protocols']
        if 'tcp' in protocols:
            tcp_count += 1
        if 'udp' in protocols:
            udp_count += 1

    if proto == 'TCP':
        return f"TCP={tcp_count}"
    elif proto == 'UDP':
        return f"UDP={udp_count}"
    elif proto == 'TCPUDP':
        return f"TCP={tcp_count}\nUDP={udp_count}"

    return "Invalid <proto>"


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] == '':
        print("Usage: server <req_code>")
        exit(1)
    req_code = sys.argv[1]
    start_server(req_code)
