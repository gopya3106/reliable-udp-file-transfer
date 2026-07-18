# Reliable UDP File Transfer System

A reliable file/message delivery system built on top of UDP, implementing custom
Automatic Repeat reQuest (ARQ) mechanisms — Stop-and-Wait and Go-Back-N — to
guarantee delivery despite UDP's inherent unreliability (packet loss, reordering,
delays).

UDP alone offers no delivery guarantees. This project adds those guarantees back
in application code using sequence numbers, acknowledgments (ACKs), timeouts,
and retransmission, without falling back to TCP.

## Features

- **Custom packet protocol** — JSON-based packets (`type`, `seq`, `data`) for
  `JOIN`, `MSG`, and `ACK` messages
- **ARQ-based reliability** — Stop-and-Wait and Go-Back-N retransmission logic
  to recover from simulated packet loss
- **Sequence numbering & acknowledgments** — every message is tagged with a
  sequence number and tracked until acknowledged
- **Retransmission with retry limits** — unacknowledged packets are resent up
  to a configurable number of attempts before giving up
- **Message encryption** — payloads are encrypted (Fernet symmetric encryption)
  before transmission and decrypted on receipt
- **Multi-client architecture** — a central server can broadcast messages to
  multiple connected clients and track per-client acknowledgment state
- **Logging** — server and client activity is logged to file for inspection
  and debugging

## Project Structure

```
rgn/
├── server.py       # UDP server: accepts client JOINs, broadcasts messages, tracks ACKs, retransmits
├── client.py       # UDP client: joins the server, receives messages, sends ACKs
├── protocol.py     # Packet creation/parsing (JSON encode/decode)
├── config.py       # Shared configuration (host, port, timeouts, retry limits, simulated loss rate)
├── security.py     # Message encryption/decryption (Fernet)
└── README.md
```

## Requirements

- Python 3.8+
- [`cryptography`](https://pypi.org/project/cryptography/) package

Install dependencies:

```bash
pip install cryptography
```

## Configuration

Connection and reliability parameters live in `config.py`:

| Setting                  | Description                                    |
|---------------------------|------------------------------------------------|
| `SERVER_HOST`             | Host the server binds to (default `127.0.0.1`) |
| `SERVER_PORT`             | UDP port used by server and clients            |
| `BUFFER_SIZE`             | Max UDP packet size read per call              |
| `TIMEOUT`                 | Seconds to wait for an ACK before retrying      |
| `MAX_RETRIES`             | Max retransmission attempts per packet          |
| `PACKET_LOSS_PROBABILITY` | Simulated packet loss rate for testing          |

## Usage

**1. Start the server** (in one terminal):

```bash
python server.py
```

**2. Start one or more clients** (in separate terminals):

```bash
python client.py
```

Each client will prompt for a client ID, then join the server and listen for
incoming messages. Received messages are decrypted, logged to
`<client_id>_notifications.log`, and acknowledged back to the server.

**3. Send a message from the server** — messages sent from the server are
encrypted, sequenced, logged to `notifications.log`, and retransmitted to any
client that hasn't acknowledged receipt within the timeout window, up to
`MAX_RETRIES` attempts.

## How It Works

1. A client sends a `JOIN` packet to register with the server.
2. The server sends `MSG` packets to all joined clients, each tagged with an
   incrementing sequence number.
3. Each client decrypts and logs the message, then replies with an `ACK`
   carrying the same sequence number.
4. The server tracks which clients have acknowledged each sequence number. If
   an ACK isn't received within `TIMEOUT` seconds, the server retransmits —
   up to `MAX_RETRIES` times — implementing the ARQ reliability guarantee.

## Security Note

`security.py` currently uses a fixed, hardcoded encryption key for
demonstration purposes. For any real-world use, generate the key at runtime
or load it from an environment variable / secrets manager rather than
committing it to source control.

## Notes

- Log files (`*.log`) and Python bytecode (`__pycache__/`) are excluded from
  version control via `.gitignore`.
- This project was built as an exploration of transport-layer reliability
  concepts (sequence numbering, ACKs, checksums, retransmission) typically
  handled by TCP, reimplemented manually over UDP with a client-server
  socket architecture.
