import socket
import sys
from packet import Packet


def receive_packets(data_port, emulator_addr, out_path, buffer_size):
    """
    Function to receive packets from the sender via the network emulator.
    """
    # Create a UDP socket and bind it to the data port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', data_port))
        # Continue with socket operations if bind is successful
    except OSError as e:
        print(f"Receiver data_port {data_port}: {e.strerror}")
        exit(1)

    buffer = {}
    base = 0

    # Open log file for packet arrivals and file for output data
    try:
        log_arrival = open("arrival.log", "w")
    except OSError as e:
        print(f"arrival.log: {e.strerror}")
        exit(1)
    try:
        out_file = open(out_path, "w")
    except OSError as e:
        print(f"{out_path}: {e.strerror}")
        exit(1)

    # Receive packets from the sender
    while True:
        packet_data = sock.recv(1024)
        packet = Packet(packet_data)
        print(f"Received packet: {packet.seqnum}")

        if packet.typ == 2:  # End of Transmission (EOT) packet
            ack_packet = Packet(2, packet.seqnum, 0, "")
            sock.sendto(ack_packet.encode(), emulator_addr)
            log_arrival.write("EOT\n")
            break

        # Check if the packet is out of the buffer range
        if len(buffer) >= buffer_size or packet.seqnum >= base + buffer_size:
            log_arrival.write(f"{packet.seqnum}D\n")
            continue

        # Send ACK for the received packet
        ack_packet = Packet(0, packet.seqnum, 0, "")
        sock.sendto(ack_packet.encode(), emulator_addr)

        if packet.seqnum < base or packet.seqnum in buffer:
            # Write the duplicate data to the log file
            log_arrival.write(f"{packet.seqnum}D\n")
        else:
            # Write the received data to the output file
            buffer[packet.seqnum] = packet.data
            log_arrival.write(f"{packet.seqnum}B\n")
            while base in buffer:
                out_file.write(buffer[base])
                del buffer[base]
                base += 1

    log_arrival.close()
    out_file.close()
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: receiver <emulator_address> <emulator_port> <data_port> <buffer_size> <output_file>")
        sys.exit(1)

    emulator_address = sys.argv[1]
    emulator_port = int(sys.argv[2])
    data_port = int(sys.argv[3])
    buffer_size = int(sys.argv[4])
    out_path = sys.argv[5]
    emulator_addr = (emulator_address, emulator_port)

    # Check if emulator_port is valid
    if emulator_port < 1 or emulator_port > 65535:
        print("Error: emulator_port must be in the range [1, 65535]")
        exit(1)

    # Check if ack_port is valid
    if data_port < 1 or data_port > 65535:
        print("Error: data_port must be in the range [1, 65535]")
        exit(1)

    # Check if emulator_address is valid
    try:
        socket.gethostbyname(emulator_address)
    except socket.error as e:
        print(f"Error: Could not resolve '{emulator_address}': {e.strerror}")
        exit(1)

    receive_packets(data_port, emulator_addr, out_path, buffer_size)
