import struct
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Socket import Socket
import pickle, sys, os
from authenticate import auth
from Crypto import Random
import threading
from protocal import parse, SND, DATA, REQ
IP = "167.99.180.229"
PORT = 12341

class User:
    def __init__(self):
        # LOADING KEYS
        try:
            data = pickle.load(open("data/spt/usr.pickle", "rb"))
            self.privkey = RSA.importKey(data["key"])
            self.pubkey = self.privkey.publickey()
            self.email = data["email"]

        except FileNotFoundError:
            while True:
                self.privkey = RSA.generate(2048)
                if ':' not in self.privkey.exportKey().decode():
                    break

        
            self.pubkey = self.privkey.publickey()
            while True:
                self.email = input("Email: ")
                if "@wearelcc.ca" in self.email and len(self.email.split("@")[0]) > 2:
                    break
                print("Please enter a valid LCC email")
            os.system("mkdir data && cd data/ && mkdir spt && touch spt/usr.pickle")
            with open("data/spt/usr.pickle", 'wb') as f:
                pickle.dump({"key": self.privkey.exportKey("PEM"), "email": self.email}, f)
         
        self.sock = Socket()
        self.authenticated = True
        resp = auth(self)
        if not resp[0]:
            self.authenticated = False
            print("Error in connecting {}".format(resp[1]))
            self.sock.close()
            sys.exit(1)
        self.key = resp[1]
        print(f"KEY: {self.key}")
        self.active = True
        self.que = []
        print("finished")
    def _send(self, data):
        iv = Random.new().read(AES.block_size)
        print("sending {}".format(data))
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        try:
            msg = iv + cipher.encrypt(data.encode())
        except AttributeError:
            msg = iv + cipher.encrypt(data)
        self.sock.send(msg)
    
    def send(self, msg):
        self.que.append(msg)

    def close(self):
        
        self.active = False

    def read(self, blocking = False):
        data = self.sock.read(blocking=blocking)
        if data:
            iv = data[:16]
            cipher = AES.new(self.key, AES.MODE_CFB, iv)
            return cipher.decrypt(data)[16:]
        else:
            return None
    def loop(self):
        print("starting {0} {1}".format(self.authenticated, self.active))
        while self.authenticated and self.active:
           
            if self.sock.bufferedData():
                data = self.read()
                print(f"Recevied: {data}")
                if data == None:
                    self.active = False
                    print("server disconnected")
                    continue
                packet = parse(data)
                if packet.type == RECV:
                    if self.currentScreen == packet.sender:
                        self.updateScreen()
                elif packet.type == DATA:
                    if self.currentScreen == packet.data.keys()[0]:
                        self.updateScreen(packet=packet)
                    
                self.close()
            if len(self.que) > 0:
                print(f"Sending: {self.que[0]}")
                self._send(self.que[0].construct())
                del self.que[0]
        self.sock.close()
    def getInput(self):
        while self.active and self.authenticated:
            target = input("Who would you like to text: ")
            if len(target.split("@")) == 2 and target.split("@")[1] == "wearelcc.ca" and len(target.split("@")[0]) > 2:
                self.send(f"REQ {target}")
                data = self.read(blocking=True)
                if data:
                    pickle.loads(data.decode())
    def updateScreen(packet=None):
        if packet:
            self.currentScreen = packet.data.keys()[0]
            
    def start(self):
        t1 = threading.Thread(target=self.loop)
        t1.start()


if __name__ == "__main__":
    user = User()

    user.start()
    print(1)
    user.send(REQ(target=user.email))
    print(2)
    input()
    user.close()
    
    
