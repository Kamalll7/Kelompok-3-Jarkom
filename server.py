import socket
import random

import protocol
import services

HOST = ""
PORT = 12000
WRONG_PROBABILITY = 0.25  # peluang server sengaja mengirim jawaban salah

# status layanan bersifat global, dibagi ke semua koneksi klien
service_status = {name: True for name in protocol.ALL_SERVICES}


def compute_result(service, payload):
    if service == protocol.SERVICE_COUNT_CHAR:
        return services.count_char(payload)
    if service == protocol.SERVICE_COUNT_WORD:
        return services.count_word(payload)
    if service == protocol.SERVICE_REVERSE_STRING:
        return services.reverse_string(payload)
    if service == protocol.SERVICE_REMOVE_VOWEL:
        return services.remove_vowel(payload)
    det, inv = services.matrix_det_inv(payload)
    return {"determinant": det, "inverse": inv}


def fake_result(service, correct):
    if service == protocol.SERVICE_MATRIX_DET_INV:
        fake_det = correct["determinant"] + random.choice([-2, -1, 1, 2])
        fake_inv = correct["inverse"]
        if fake_inv is not None:
            fake_inv = [row[:] for row in fake_inv]
            r, c = random.randrange(3), random.randrange(3)
            fake_inv[r][c] = round(fake_inv[r][c] + random.uniform(0.5, 2), 4)
        return {"determinant": fake_det, "inverse": fake_inv}
    if isinstance(correct, str):
        return correct + random.choice(["x", "9", "?"])
    return correct + random.choice([1, 2, 3])


def validate_payload(service, payload):
    if service == protocol.SERVICE_MATRIX_DET_INV:
        if not isinstance(payload, list) or len(payload) != 3:
            return False
        for row in payload:
            if not isinstance(row, list) or len(row) != 3:
                return False
            if not all(isinstance(v, (int, float)) for v in row):
                return False
        return True
    return isinstance(payload, str)


def handle_client(conn, addr):
    rfile = conn.makefile("r", encoding="utf-8")
    wfile = conn.makefile("w", encoding="utf-8")
    print(f"Klien terhubung: {addr}")
    shutdown = False

    try:
        while True:
            try:
                msg = protocol.read_message(rfile)
            except ValueError:
                protocol.send_message(wfile, {
                    "msg_type": protocol.MSG_ERROR,
                    "message": "Format JSON tidak valid."
                })
                continue
            if msg is None:
                break

            if msg.get("msg_type") != protocol.MSG_REQUEST:
                protocol.send_message(wfile, {
                    "msg_type": protocol.MSG_ERROR,
                    "message": "msg_type harus REQUEST."
                })
                continue

            service = msg.get("service")
            payload = msg.get("payload")

            if service not in protocol.ALL_SERVICES:
                protocol.send_message(wfile, {
                    "msg_type": protocol.MSG_ERROR,
                    "service": service,
                    "message": "Layanan tidak dikenal."
                })
                continue

            if not service_status[service]:
                protocol.send_message(wfile, {
                    "msg_type": protocol.MSG_RESPONSE,
                    "service": service,
                    "status": protocol.STATUS_SERVICE_DISABLED,
                    "message": f"Layanan {service} sedang tidak aktif."
                })
                continue

            if not validate_payload(service, payload):
                protocol.send_message(wfile, {
                    "msg_type": protocol.MSG_ERROR,
                    "service": service,
                    "message": "Payload tidak sesuai format yang diharapkan."
                })
                continue

            correct = compute_result(service, payload)
            result = fake_result(service, correct) if random.random() < WRONG_PROBABILITY else correct

            protocol.send_message(wfile, {
                "msg_type": protocol.MSG_RESPONSE,
                "service": service,
                "status": protocol.STATUS_OK,
                "result": result
            })

            try:
                ack = protocol.read_message(rfile)
            except ValueError:
                continue
            if ack is None:
                break
            if ack.get("msg_type") != protocol.MSG_ACK:
                continue

            if ack.get("status") == protocol.STATUS_INCORRECT:
                service_status[service] = False
                print(f"Layanan {service} dinonaktifkan.")
                protocol.send_message(wfile, {
                    "msg_type": protocol.MSG_SERVICE_DISABLED_NOTICE,
                    "service": service,
                    "message": f"Layanan {service} telah dinonaktifkan."
                })

                if not any(service_status.values()):
                    protocol.send_message(wfile, {
                        "msg_type": protocol.MSG_SERVER_SHUTDOWN,
                        "message": "Semua layanan telah dinonaktifkan. Server berhenti."
                    })
                    print("Semua layanan nonaktif, server berhenti.")
                    shutdown = True
                    break
    finally:
        rfile.close()
        wfile.close()
        conn.close()
        print(f"Koneksi dengan {addr} ditutup.")

    return shutdown


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server siap menerima koneksi di port {PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            if handle_client(conn, addr):
                break
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
