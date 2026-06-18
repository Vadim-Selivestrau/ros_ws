#!/usr/bin/env python3
import socket
import threading

HOST = '0.0.0.0'
PORT = 8081
GST_PORT = 8090

def handle_client(client_socket):
    try:
        header = (
            "HTTP/1.0 200 OK\r\n"
            "Server: GStreamer-MJPEG\r\n"
            "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n"
            "\r\n"
        )
        client_socket.send(header.encode())

        gst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        gst_socket.connect(('127.0.0.1', GST_PORT))

        while True:
            data = gst_socket.recv(4096)
            if not data:
                break
            try:
                client_socket.send(data)
            except BrokenPipeError:
                break

    except Exception as e:
        print("Client error:", e)

    finally:
        try:
            gst_socket.close()
        except:
            pass
        try:
            client_socket.close()
        except:
            pass


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(f"HTTP MJPEG server running on http://{HOST}:{PORT}")

while True:
    client, addr = server.accept()
    threading.Thread(target=handle_client, args=(client,), daemon=True).start()
