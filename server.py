import socket
import threading
import time
import random

from config import *
from protocol import create_packet, parse_packet
from security import encrypt_message

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))

clients = {}
acknowledged = {}

lock = threading.Lock()
sequence_number = 0


def log_notification(message, seq):
    with open("notifications.log", "a") as f:
        f.write(f"{time.ctime()} | Seq {seq} | {message}\n")


def listen_for_clients():
    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        packet = parse_packet(data)

        if packet["type"] == "JOIN":
            client_id = packet["data"]
            with lock:
                clients[addr] = client_id
            print(f"[JOIN] {client_id} joined from {addr}")

        elif packet["type"] == "ACK":
            seq = packet["seq"]
            with lock:
                if seq in acknowledged:
                    acknowledged[seq].add(addr)


def send_notification(message):
    global sequence_number
    sequence_number += 1
    seq = sequence_number

    encrypted_msg = encrypt_message(message).decode()
    packet = create_packet("MSG", seq, encrypted_msg)

    with lock:
        acknowledged[seq] = set()
        current_clients = list(clients.keys())

    log_notification(message, seq)

    retries = 0

    while retries < MAX_RETRIES:
        print(f"[SEND] Seq {seq}, Attempt {retries+1}")

        for client in current_clients:
            if random.random() > PACKET_LOSS_PROBABILITY:
                server_socket.sendto(packet, client)
            else:
                print(f"[LOSS SIM] Packet to {client} dropped")

        time.sleep(TIMEOUT)

        with lock:
            acked = acknowledged[seq]

        if len(acked) == len(current_clients):
            print(f"[SUCCESS] All clients ACKed Seq {seq}")
            break
        else:
            print(f"[RETRY] Missing ACKs: {len(current_clients) - len(acked)}")
            retries += 1

    if retries == MAX_RETRIES:
        print("[WARNING] Removing unresponsive clients")
        with lock:
            for client in current_clients:
                if client not in acknowledged[seq]:
                    print(f"[REMOVE] {clients[client]}")
                    del clients[client]

    with lock:
        del acknowledged[seq]


threading.Thread(target=listen_for_clients, daemon=True).start()

print("Server running...")

while True:
    msg = input("Enter message: ")
    send_notification(msg)