import socket
import sys
import threading
import time
from packet import Packet


def send_packets(ack_port, emulator_addr, file_path, window_size, timeout):
    """
    Function to send packets from the sender to the receiver via the network emulator.
    """
    # Read data from the specified file
    try:
        with open(file_path, "r") as file:
            data = file.read()
    except OSError as e:
        print(f"{file_path}: {e.strerror}")
        exit(1)

    # Create a UDP socket and bind it to the acknowledgment port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', ack_port))
        # Continue with socket operations if bind is successful
    except OSError as e:
        print(f"Sender ack_port {ack_port}: {e.strerror}")
        exit(1)

    base = 0
    lock = threading.Lock()
    acked = set()

    # Open log files for sequence numbers of packets sent and acknowledgments received
    try:
        log_seqnum = open("seqnum.log", "w")
    except OSError as e:
        print(f"seqnum.log: {e.strerror}")
        exit(1)
    try:
        log_ack = open("ack.log", "w")
    except OSError as e:
        print(f"ack.log: {e.strerror}")
        exit(1)

    # Create packets from the file data
    packets = [Packet(1, i, min(500, len(data) - i * 500), data[i * 500:(i + 1) * 500])
               for i in range((len(data) + 499) // 500)]

    def send_window():
        """
        Function to send a window of packets.
        """
        nonlocal base, acked, packets, sock, log_seqnum, lock
        while base < len(packets):
            lock.acquire()
            i = base
            # Send packets in the window
            for _ in range(window_size):
                # Skip packets that have already been acknowledged
                while i in acked:
                    i += 1
                # Break if all packets have been sent
                if i >= len(packets):
                    break
                print(f"Sending packet {packets[i].seqnum}")
                sock.sendto(packets[i].encode(), emulator_addr)
                log_seqnum.write(f"{packets[i].seqnum}\n")
                i += 1
            lock.release()
            time.sleep(timeout / 1000)

    def receive_acks():
        """
        Function to receive acknowledgments and update the sliding window.
        """
        nonlocal base, acked, packets, sock, log_ack, lock
        while base < len(packets):
            ack_packet = sock.recv(1024)
            ack = Packet(ack_packet)
            log_ack.write(f"{ack.seqnum}\n")
            lock.acquire()
            print(f"Received ACK for packet {ack.seqnum}")
            acked.add(ack.seqnum)
            # Update base based on received ACKs
            while base in acked:
                base += 1
            lock.release()

    # Start threads for sending packets and receiving ACKs
    threading.Thread(target=send_window).start()
    threading.Thread(target=receive_acks).start()

    # Wait for all packets to be acknowledged
    while base < len(packets):
        time.sleep(1)

    # Send End of Transmission (EOT) packet
    print(f"Sending packet {len(packets)} (EOT)")
    sock.sendto(Packet(2, len(packets), 0, "").encode(), emulator_addr)
    log_seqnum.write(f"EOT\n")
    while True:
        # Wait for ACK for EOT packet
        ack_packet = sock.recv(1024)
        ack = Packet(ack_packet)
        if ack.typ == 2:
            print(f"Received ACK for packet EOT")
            log_ack.write("EOT\n")
            break

    log_seqnum.close()
    log_ack.close()
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: sender <emulator_address> <emulator_port> <ack_port> <timeout> <window_size> <file_path>")
        sys.exit(1)

    emulator_address = sys.argv[1]
    emulator_port = int(sys.argv[2])
    ack_port = int(sys.argv[3])
    timeout = int(sys.argv[4])
    window_size = int(sys.argv[5])
    file_path = sys.argv[6]
    emulator_addr = (emulator_address, emulator_port)

    # Check if emulator_port is valid
    if emulator_port < 1 or emulator_port > 65535:
        print("Error: emulator_port must be in the range [1, 65535]")
        exit(1)

    # Check if ack_port is valid
    if ack_port < 1 or ack_port > 65535:
        print("Error: ack_port must be in the range [1, 65535]")
        exit(1)

    # Check if emulator_address is valid
    try:
        socket.gethostbyname(emulator_address)
    except socket.error as e:
        print(f"Error: Could not resolve '{emulator_address}': {e.strerror}")
        exit(1)

    send_packets(ack_port, emulator_addr, file_path, window_size, timeout)
