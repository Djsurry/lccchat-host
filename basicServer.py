import Stockings, socket, os, struct, sqlite3, threading, time
from Socket import Socket
from authenticateServer import auth
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from base64 import b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
from protocal import SND, REQ, STA, parse, RECV, DATA
import pickle, json
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', filename='/var/log/lccchat.log', level=logging.DEBUG)

["SND email msg", "REQ email", "STA bool"]

# TO DO
# 1. CHECK FOR CLIENTS WHO HAVE DISCONNECTED AND MAKE active=False
# 2. debug


def getHistory(user, recv):
    print('LOL')
    conn = sqlite3.connect("/var/www/lccchat/lccchat/lccchat.db")
    c = conn.cursor()
    logging.info("THE THING: {}".format(list(c.execute("select history from users where email=?", (user,)))))
    path = list(c.execute("select history from users where email=?", (user,)))[0][0]
    history = json.load(open(path))
    conn.close()
    if recv not in history.keys():
        return {recv: []}
    else:
        return history[recv]

def addToHistroy(user, recv, msg):
    conn = sqlite3.connect("/var/www/lccchat/lccchat/lccchat.db")
    c = conn.cursor()
    path = list(c.execute("select history from users where email=?", (user,)))[0]
    logging.info(path)
    history = json.load(open(path))
    if recv in history.keys():
        histroy[recv].append((True, msg))
    else:
        history[recv] = [(True, msg)]
    path = c.execute("select history from users where email=?", (recv,))
    history = json.load(open(path))
    if user in history.keys():
        histroy[user].append((False, msg))
    else:
        history[user] = [(False, msg)]
    conn.close()

class Host(threading.Thread):
    def __init__(self, conn):
        super().__init__()
        print("CREATED")
        self.socket = conn
        self.hostname = "me"
        logging.info("starting auth")
        resp = auth(self)
        print("got {}".format(resp))
        logging.info("finished auth, got {}".format(resp))
        self.que = []
        self.outgoing = []
        if resp:
            self.email = resp[1]
            self.key = resp[0]
            self.authenticated = True
            self.active = True
        else:
            self.authenticated = False


    def _send(self, data):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        try:
            msg = iv + cipher.encrypt(data.encode())
        except AttributeError:
            msg = iv + cipher.encrypt(data)
        self.socket.send(msg)
    
    def send(self, msg):
        logging.info("adding message {0} to que of {1}".format(msg, self.hostname))
        self.que.append(msg)

    def close(self):
        self.active = False

    def addToQue(self, packet):
        self.outgoing.append(packet)
    def read(self):
        data = self.socket.read()
        if not data:
            return None
        iv = data[:16]
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher.decrypt(data)[16:].decode()
    def run(self):
        logging.info("Starting loop")
        while self.authenticated and self.active:

            if self.socket.bufferedData():
                data = self.read()
                if data == None:
                    self.close()
                    logging.info("host {} dc".format(self.hostname))
                    continue
                logging.info("{0} received {1}".format(self.hostname, data))
                packet = parse(data)
                if type(packet) == REQ:
                    history = getHistory(self.email, packet.target)
                    new = DATA(data=history)
                    self.send(new.construct())
                elif type(packet) == SND:
                    msg = packet.content
                    target = packet.content
                    new = RECV(sender=self.email, content=msg, target=target)
                    addToHistroy(new.sender, new.target, new.content)
                    self.addToQue(new)

            if len(self.que) > 0:
                logging.info(f"Sending: {self.que[0]}")
                self._send(self.que[0])
                del self.que[0]
        self.socket.close()

class Server:
    def __init__(self):
        self.port = 12341
        self.socket = Socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.socket.bind(('', self.port))
        self.socket.listen(5)
        os.system("sudo ufw allow {}".format(self.port))
        self.clients = []
        self.active = False
        self.que = []
    def run(self):
        while self.active:
            try:
                conn, addr = self.socket.accept()
                logging.info(f"Connected to {addr}")
                t = Host(conn)
                t.start()
                self.clients.append(t)
            except:
                continue
    
    def manageMessages(self):
        while self.active:
            for client in self.clients:
                if len(client.outgoing) > 0:
                    if client.outgoing[0].type == RECV:
                        sent = False
                        for c in self.clients:
                            if c.email == client.outgoing[0].target:
                                c.send(client.outgoing[0].construct())
                                sent = True
                        if sent:
                            del client.outgoing[0]
     
    def close(self):
        self.active = False
        self.socket.close()
        for i in self.clients:
            i.close()
        for i in self.clients:
            i.join()
        os.system("sudo ufw deny {}".format(self.port))
    def start(self):
        t = threading.Thread(target=self.run)
        self.active = True
        t.start()
    def serverWideMessage(self, msg):
        for i in self.clients:

            i.send(msg)

if __name__ == "__main__":
    server = Server()
    server.start()

    input()
    server.close()
