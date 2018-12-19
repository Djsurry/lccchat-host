import struct
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Socket import Socket
import pickle, sys
from authenticate import auth
from Crypto import Random
from display import display
import threading
IP = "167.99.180.229"
PORT = 12341


def parse(data):
    try:
        if type(data) == bytes:

        if "RECV" in data:
        
            target = data.split()[1]
            msg = ' '.join(data.split()[2:])
            packet =  SND(target=target, msg=msg)
        
        elif "DATA" in data:
            
            raw = data.split()[1]
            packet = DATA(raw=raw)
        
        elif "STA" in data:

            status = data.split()[1]
            if status.lower() == "true":
                packet =  STA(status=True)
    except:



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
   
    def _send(self, data):
        iv = Random.new().read(AES.block_size)
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
        
        while self.authenticated and self.active:
           
            if self.sock.bufferedData():
                data = self.read()
                print(f"Recevied: {data}")
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
                self._send(self.que[0])
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
    input()
    user.close()
    
    
