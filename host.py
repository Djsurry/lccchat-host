import socket, Stockings
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes



def authenticate(sock, email, pubkey):
    sock._write(email)
    resp = None
    while resp == None:
        resp = sock._read()
    if resp == 'verify':
        return "verify"
    elif resp == '':
        return "session terminated"
    sock._write(str(pubkey))
    resp = None
    while resp == None:
        resp = sock._read()
    if resp == 'Failed: pubkey':
        return "Failed: pubkey"
    elif resp == '':
        return "session terminated"
    sock._write("all good")
    key = sock._read()
    if key == '':
        return "session terminated"
    return key


class Sock(Stockings.Stocking):
    def __init__(self, email, pubkey, privkey):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((IP, PORT))
            self.connected = True
        except:
            self.connected = False
        Stockings.Stocking.__init__(self, self.socket)
        self.email = email
        self.pubkey = privkey.publickey().exportKey('PEM')
        self.privkey = privkey
        self.key = None
        self.needs_email_verification = False
    
    def preWrite(self, msg):
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CFB)
        txt = iv + cipher.encrypt(data)
        return txt.decode('utf-8')
    
        
    def postRead(self, data):
        iv = msg[:16]
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        p = cipher.decrypt(msg)
        plain = p[16:]
        return plain
    
    def handshake(self):
        a = authenticate(self.socket, self.email, self.pubkey)
        if a in ["Failed: pubkey", "session terminated", "verify", "Server Down"]:
            if a == "verify":
                self.needs_email_verification = True
            return False    
        self.key = self.privkey.decrypt(a)
        self.privkey = None
        self.pubkey = None
        return True

def main():
    #email = input("Email: ")
    #pubkey = input("pubkey: ")
    #privkey = input("privkey: ")
    email = "dsurry@wearelcc.ca"
    pubkey = "dfsjidflsdjkhflewiufl"
    privkey = "sjhdalfjdsahlfakjh"
    sock = Sock(email, pubkey, privkey)
    print("WORKING")

main()
    
        
        
        
        
        
