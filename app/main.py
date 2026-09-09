import socket
import threading


store = {}
store_lock = threading.Lock()


def read_line(rfile):
    return rfile.readline().rstrip(b"\r\n")


def parse_command(rfile):
    line = read_line(rfile)
    if not line:
        return None

    assert line[0:1] == b"*", f"Expected array, got {line}"
    num_elements = int(line[1:])

    args = []
    for _ in range(num_elements):
        bulk_header = read_line(rfile)
        assert bulk_header[0:1] == b"$", f"Expected bulk string, got {bulk_header}"
        length = int(bulk_header[1:])
        data = rfile.read(length)
        rfile.read(2)
        args.append(data.decode())

    return args


def encode_bulk_string(s):
    return f"${len(s)}\r\n{s}\r\n".encode()


def encode_simple_string(s):
    return f"+{s}\r\n".encode()


def encode_null_bulk_string():
    return b"$-1\r\n"


def handle_client(connection):
    rfile = connection.makefile("rb")
    while True:
        args = parse_command(rfile)
        if args is None:
            break

        command = args[0].upper()

        if command == "PING":
            connection.sendall(b"+PONG\r\n")

        elif command == "ECHO":
            connection.sendall(encode_bulk_string(args[1]))

        elif command == "SET":
            key, value = args[1], args[2]
            with store_lock:
                store[key] = value
            connection.sendall(encode_simple_string("OK"))

        elif command == "GET":
            key = args[1]
            with store_lock:
                value = store.get(key)
            if value is None:
                connection.sendall(encode_null_bulk_string())
            else:
                connection.sendall(encode_bulk_string(value))

    connection.close()


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        connection, address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(connection,))
        thread.start()


if __name__ == "__main__":
    main()