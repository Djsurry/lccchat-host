import pickle


class Request:
    def __init__(self, target=None, content=None, data=None, status=None, sender=None):
        self.target = target
        self.content = content
        self.raw = data
        self.data = pickle.loads(self.raw) if self.raw else None
        self.status = status
        self.sender = sender



class STA(Request):
    def __init__(self, status=False):
        self.type = STA
        super().__init__(status=status)

    def construct(self):
        msg = f'STA {self.status}'


class SND(Request):
    def __init__(self, target=None, content=None):
        self.type = SND
        super().__init__(target=target, content=content)

    def construct(self):
        msg = f'SND {self.target} {self.content}'
        return msg


class RECV(Request):
    def __init__(self, sender=None, content=None, target=None):
        self.type = RECV
        super().__init__(sender=sender, content=content, target=target)

    def construct(self):
        msg = f'RECV {self.sender} {self.target} {self.content}'
        return msg


class DATA(Request):
    def __init__(self, data=None):
        self.type = DATA
        super().__init__(data=data)

    def construct(self):
        msg = b'DATA' + pickle.dumps(self.data)
        return msg


class REQ(Request):
    def __init__(self, target=None):
        self.type = REQ
        super().__init__(target=target)

    def construct(self):
        msg = f'REQ {self.target}'
        return msg


def parse(data):
    if type(data) == bytes:

        classifer = data[:4]

        if classifer != b"DATA":
            data = data.decode()

        else:
            packet = DATA(data=data[4:])

            return packet
    classifier = data.split()[0]
    if classifier == "REQ":
        packet = REQ(target=data.split()[1])
    elif classifier == "RECV":
        packet = RECV(sender=data.split()[1], target=data.split()[2], content=' '.join(data.split()[3:]))
    elif classifier == "SND":
        packet = SND(target=data.split()[1], content=' '.join(data.split()[2:]))
    elif classifier == "STA":
        packet = STA(status=data.split()[1])
    return packet


d = pickle.dumps({"some cool stuff": ["wow", "this", "is", "a", "list", "pog"]})

data = b"DATA" + d
if __name__ == "__main__":
    packet = parse(data)
    print(packet.data)



