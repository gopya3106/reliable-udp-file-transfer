import socket
import threading

from config import *
from protocol import create_packet, parse_packet
from security import decrypt_message

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_id = input("Enter client ID: ")

def log_client_message(seq, message):
    with open(f"{client_id}_notifications.log", "a") as f:
        f.write(f"{seq} | {message}\n")


# Send JOIN
join_packet = create_packet("JOIN", 0, client_id)
client_socket.sendto(join_packet, (SERVER_HOST, SERVER_PORT))


def listen():
    while True:
        data, addr = client_socket.recvfrom(BUFFER_SIZE)
        packet = parse_packet(data)

        if packet["type"] == "MSG":
            seq = packet["seq"]

            encrypted_data = packet["data"].encode()
            message = decrypt_message(encrypted_data)

            print(f"[RECEIVED] Seq {seq}: {message}")

            log_client_message(seq, message)

            ack_packet = create_packet("ACK", seq, "")
            client_socket.sendto(ack_packet, addr)


threading.Thread(target=listen, daemon=True).start()

while True:
    pass