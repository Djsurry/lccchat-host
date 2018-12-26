import socket, struct, select


class Socket:
    def __init__(self, s=None):
        '''default create a new socket, or wrap an existing one.
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) if s is None else s

    def connect(self, addr):
        self.sock.connect(addr)

    def bind(self, addr):
        self.sock.bind(addr)

    def listen(self, n):
        self.sock.listen(n)

    def accept(self, blocking=False):
        if blocking:
            c, a = self.sock.accept()
            # Wrap the client socket in a Socket.
            return Socket(c), a
        if self.bufferedData():
            c, a = self.sock.accept()
            # Wrap the client socket in a Socket.
            return Socket(c), a
        else:
            return None, None

    def bufferedData(self):
        r, _, _ = select.select([self.sock], [], [], 0)
        if r:
            return True
        return False

    def read(self, blocking=False):
        r, _, _ = select.select([self.sock], [], [], 0)
        if not r and not blocking:
            return None
        l = self.sock.recv(struct.calcsize("I"))
        if not l:
            return None
        length = struct.unpack("I", l)[0]

        msg = self.sock.recv(length)
        try:
            return msg.decode()
        except UnicodeDecodeError:
            return msg

    def send(self, msg):
        if type(msg) == str:
            self.sock.sendall(struct.pack("I", len(msg.encode())) + msg.encode())
        elif type(msg) == bytes:
            self.sock.sendall(struct.pack("I", len(msg)) + msg)
        else:
            raise TypeError("msg must be bytes or str not {}".format(type(msg)))

    def close(self):
        self.sock.shutdown()
        self.sock.close()    
