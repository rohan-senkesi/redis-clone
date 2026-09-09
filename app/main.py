import socket
import threading


def read_line(rfile):
    """Read one line (RESP header), stripped of the trailing \r\n."""
    return rfile.readline().rstrip(b"\r\n")


def parse_command(rfile):
    """Parse one RESP-encoded command array into a list of strings."""
    line = read_line(rfile)
    if not line:
        return None  # client closed connection

    # line looks like b"*2" — array of 2 elements
    assert line[0:1] == b"*", f"Expected array, got {line}"
    num_elements = int(line[1:])

    args = []
    for _ in range(num_elements):
        bulk_header = read_line(rfile)  # e.g. b"$4"
        assert bulk_header[0:1] == b"$", f"Expected bulk string, got {bulk_header}"
        length = int(bulk_header[1:])
        data = rfile.read(length)  # read exactly `length` bytes
        rfile.read(2)  # consume the trailing \r\n after the data
        args.append(data.decode())

    return args


def encode_bulk_string(s):
    """Encode a Python string as a RESP bulk string."""
    return f"${len(s)}\r\n{s}\r\n".encode()


def handle_client(connection):
    rfile = connection.makefile("rb")  # read in binary mode, buffered
    while True:
        args = parse_command(rfile)
        if args is None:
            break

        command = args[0].upper()

        if command == "PING":
            connection.sendall(b"+PONG\r\n")
        elif command == "ECHO":
            response = encode_bulk_string(args[1])
            connection.sendall(response)

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