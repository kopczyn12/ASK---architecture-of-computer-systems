# Michał Kopczyński 184817
# Maksymilian Terebus 181595
# ACiR VI sem
# ASK L6 (serwer)
import socket
import threading

players = [[None, "1"], [None, "-1"]]


# Handling the client
def handle_client(conn, addr, color):
    print(f"Connected with a new client: {addr}")

    while True:
        message = conn.recv(1024).decode()
        if not message:
            break
        else:
            print(f"Received from {addr}: {message}")

            # Forward the message to the other player
            for player in players:
                if player[0] != conn and player[0] is not None:
                    player[0].send(message.encode())
        print(f'Message from {addr} sent')

    print(f"Player ({color}) disconnected")
    for player in players:
        if player[0] == conn:
            player[0] = None
            break
    conn.close()


def main():
    print('Server window')

    host = socket.gethostbyname(socket.gethostname())
    port = 50000

    # Creating server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        print(f"Server runs on {host}:{port}")
        sock.listen()

        while True:
            conn, addr = sock.accept()
            for player in players:
                if player[0] is None:
                    player[0] = conn
                    # Send the color to the client
                    conn.send((player[1] + '\n').encode())
                    if player[1] == "1":
                        print(f"Player {player[0]} plays as white.")
                    else:
                        print(f"Player {player[0]} plays as black.")

                    # Creating a thread for each client
                    thread = threading.Thread(target=handle_client, args=(conn, addr, player[1]))
                    thread.start()

                    # Refresh signal after both players connect
                    if all(p[0] is not None for p in players):
                        for player in players:
                            player[0].send("refresh".encode())
                    break
            else:
                print("Already have two players, can't accept more.")
                print(f"Disconnecting {player[0]}")
                conn.close()
                continue


if __name__ == "__main__":
    main()
