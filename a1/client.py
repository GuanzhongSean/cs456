import socket
import sys


def start_client(server_address, n_port, req_code, proto, filename):
    # Check the trace file is valid first
    with open(filename) as file:
        trace_data = file.read()

    # Create a UDP socket for negotiation
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send UPLOAD request to the server
    upload_request = f"UPLOAD {req_code} {proto}"
    udp_socket.sendto(upload_request.encode(), (server_address, int(n_port)))

    # Receive the random port number from the server
    r_port = int(udp_socket.recv(1024).decode())
    if r_port == 0:
        print("Server rejected the request.")
        exit(1)

    # Create a TCP socket for the transaction and send trace file to the server
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((server_address, r_port))
    tcp_socket.sendall(trace_data.encode())

    # Receive the packet counts from the server
    counts = tcp_socket.recv(1024).decode()
    print(counts)

    # Close the sockets
    tcp_socket.close()
    udp_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: client <server_address> <n_port> <req_code> <proto> <filename>")
        exit(1)

    server_address = sys.argv[1]
    n_port = sys.argv[2]
    req_code = sys.argv[3]
    proto = sys.argv[4]
    filename = sys.argv[5]

    start_client(server_address, n_port, req_code, proto, filename)
