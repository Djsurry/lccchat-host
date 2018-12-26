
import time, socket, string, random, sqlite3, os, struct
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from base64 import b64encode
from Crypto.Cipher import PKCS1_OAEP
from Email import sendEmail

IP = "167.99.180.229"
PORT = 12341
  

def verify(email, pubkey):
    conn = sqlite3.connect("/var/www/lccchat/lccchat/lccchat.db")
    c = conn.cursor()
    e = [n for n in c.execute("select email from users where email=?", (email,))]
    if not e:
        hash = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=15))
        c.execute("insert into users values (?, ?, ?, ?, ?)", (email, pubkey, "0 ", "", hash))
        conn.commit()
        conn.close()
        link = "https://lccchat.me/verify?token={}".format(hash)
        return link

    users = [n for n in c.execute("select pubkey, hash from users where email=?", (email,))][0]
    pubkeys = users[0].split(':')
    hashes = users[1].split(' ')
    if pubkey in pubkeys:
        conn.close()
        return "https://lccchat.me/verify?token={}".format(hashes[pubkeys.index(pubkey)])
    pubkeys.append(pubkey)
    hashes.append(''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=15)))
    s = [n[0] for n in c.execute('select verified from users where email=?', (email,))][0]
    s += "0 "
    ps = ''
    for i in pubkeys:
        ps += i
        ps += ':'
    hs = ''
    for i in hashes:
        hs += i
        hs += ' '
    c.execute('update users set hash = ?, pubkey = ?, verified = ? where email=?', (hs, ps, s, email))
    conn.commit()
    conn.close()
    return "https://lccchat.me/verify?token={}".format(hashes[-1])

def auth(host):
    conn = sqlite3.connect("/var/www/lccchat/lccchat/lccchat.db")
    c = conn.cursor()
    print("STARTING AUTH PROCESS")
    email = host.socket.read(blocking=True)
    print(1)
    pubkey = host.socket.read(blocking=True)
    print(2)
    # if not email or not pubkey:
    #     print("EMAIL OR PUBKEY NOT SENT")
    #     return False
    
    a = [n for n in c.execute("select email from users where email=?", (email,))]
    print(3)
    if not a:

        sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
        host.socket.send("ERR VERIFY {}".format(email))
        print("NOT ON RECORD")
        return False
    print(4)
    r = [n for n in c.execute("select pubkey, verified from users where email=?", (email,))][0]
    print(f"r1: {r}")
    print(5)
    p = r[0].split(":")
    print(6)
    print(f"r1: {r[1]}")
    print(f"p: {p}")
    a = [int(n) for n in r[1].split()]

    print(7)
    if pubkey in p:
        print("ASDAS")
        print(f"a: {a}")
        print(f"index: {p.index(pubkey)}")

        # INDEX ERROR HERE. LIST HAS ONLY ONE ITEM BUT THE INDEX IS 1
        if a[p.index(pubkey)] == 0:
            print("VERIFY NEEDED")
            sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
            host.socket.send("ERR VERIFY {}".format(email))
            return False
        else:

            key = os.urandom(16)
            print(key)
            cipher = PKCS1_OAEP.new(RSA.importKey(pubkey))

            ciphertext = cipher.encrypt(key)
  
            host.socket.send(b"VER KEY")
            host.socket.send(ciphertext)

            print("SENT KEY")
            return key, email
    
    else:
        print("3123")
        sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
        host.socket.send("ERR VERIFY {}".format(email))
        print("PUBKEY NOT IN LISTED PUBKEYS")
        return False
    