import time, socket
from Crypto.Cipher import PKCS1_OAEP

IP = "167.99.180.229"
PORT = 12341

def auth(user):
    # MAKING SURE SERVER IS UP
    try:
  
        user.sock.sock.settimeout(1)
        user.sock.sock.connect((IP, PORT))
        
    except Exception as e:
        print(e.args)
        return False, "Server down"

    user.sock.sock.settimeout(None)

    
    # SENDING ALL DATA
    print("SENDING EMAIL")
    user.sock.send(user.email)
    print("SENDING KEY")
    user.sock.send(user.pubkey.exportKey("PEM"))
    print("finished sending")
    # WAIT FOR RESP
    
    resp = user.sock.read(blocking=True)
    print(f"GOT RESP: {resp}")
    # CHECKING FOR ERROR

    try:
        if "ERR" in resp:
            return False, resp.split("ERR")[1]
    except TypeError:
        pass
    
    

    key = user.sock.read(blocking=True)
    print("DAB ON EM {}".format(key))
    cipher = PKCS1_OAEP.new(user.privkey)
  
  
    return True, cipher.decrypt(key)