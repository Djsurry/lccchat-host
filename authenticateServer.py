
import time, socket, string, random, sqlite3, os, struct, hashlib, sys
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from base64 import b64encode
from Crypto.Cipher import PKCS1_OAEP
from Email import sendEmail

IP = "167.99.180.229"
PORT = 12341
def write(s):
    sys.stdout.write(s + '\n')
    sys.stdout.flush()

def hash_string(string):
    """
    Return a SHA-256 hash of the given string
    """
    return hashlib.sha256(string.encode('utf-8')).hexdigest()


def verify(email, pubkey):
    conn = sqlite3.connect("/var/www/lccchat/lccchat/lccchat.db")
    c = conn.cursor()
    e = [n for n in c.execute("select email from users where email=?", (hash_string(email),))]
    if not e:
        sys.stdout.write("MAKING NEW ENTRY")
        hash = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=15))
        c.execute("insert into users values (?, ?, ?, ?, ?)", (hash_string(email), pubkey, "0 ", "", hash))
        conn.commit()
        conn.close()
        link = "https://lccchat.me/verify?token={}".format(hash)
        return link

    users = [n for n in c.execute("select pubkey, hash from users where email=?", (hash_string(email),))][0]
    pubkeys = users[0].split(':')
    hashes = users[1].split(' ')
    if pubkey in pubkeys:
        conn.close()
        sys.stdout.write(213123123123121)
        return "https://lccchat.me/verify?token={}".format(hashes[pubkeys.index(pubkey)])
    pubkeys.append(pubkey)
    hashes.append(''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=15)))
    s = [n[0] for n in c.execute('select verified from users where email=?', (hash_string(email),))][0]
    s += "0 "
    ps = ''
    for i in pubkeys:
        ps += i
        ps += ':'
    hs = ''
    for i in hashes:
        hs += i
        hs += ' '
    c.execute('update users set hash = ?, pubkey = ?, verified = ? where email=?', (hs, ps, s, hash_string(email)))
    conn.commit()
    conn.close()
    return "https://lccchat.me/verify?token={}".format(hashes[-1])

def auth(host):
    conn = sqlite3.connect("/var/www/lccchat/lccchat/lccchat.db")
    c = conn.cursor()
    print('starting auth process')
    email = host.socket.read(blocking=True)
    sys.stdout.write("1")
    sys.stdout.flush()
    pubkey = host.socket.read(blocking=True)
    sys.stdout.write('2')
    sys.stdout.flush()
    # if not email or not pubkey:
    #     sys.stdout.write("EMAIL OR PUBKEY NOT SENT")
    #     return False
    
    a = [n for n in c.execute("select email from users where email=?", (hash_string(email),))]
    sys.stdout.write('3')
    sys.stdout.flush()

    if not a:
        write('here')
        sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
        host.socket.send("ERR VERIFY {}".format(email))
        sys.stdout.write("NOT ON RECORD")
        return False
    write(str([n for n in c.execute("select pubkey, verified from users where email=?", (hash_string(email),))][0]))
    r = [n for n in c.execute("select pubkey, verified from users where email=?", (hash_string(email),))][0]
    sys.stdout.write(f"r1: {r}")
    sys.stdout.write('5')
    sys.stdout.flush()
    p = [n for n in r[0].split(":") if n]
    sys.stdout.write('6')
    sys.stdout.write(f"r1: {r[1]}")
    sys.stdout.write(f"p: {p}")
    sys.stdout.flush()
    a = [int(n) for n in r[1].split()]

    sys.stdout.write('7')
    sys.stdout.flush()
    if pubkey in p:
        sys.stdout.write("ASDAS")
        sys.stdout.write(f"a: {a}")
        sys.stdout.write(f"index: {p.index(pubkey)}")
        sys.stdout.flush()

        if a[p.index(pubkey)] == 0:
            sys.stdout.write("VERIFY NEEDED")
            sys.stdout.flush()
            sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
            host.socket.send("ERR VERIFY {}".format(email))
            return False
        else:
            write('it worked?')
            key = os.urandom(16)

            cipher = PKCS1_OAEP.new(RSA.importKey(pubkey))

            ciphertext = cipher.encrypt(key)
            write(f'sending {ciphertext}')
            host.socket.send(b"VER KEY")
            host.socket.send(ciphertext)

            sys.stdout.write("SENT KEY")
            sys.stdout.write()
            return key, email
    
    else:
        sys.stdout.write("3123")
        sys.stdout.flush()
        sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
        host.socket.send("ERR VERIFY {}".format(email))
        sys.stdout.write("PUBKEY NOT IN LISTED PUBKEYS")
        sys.stdout.flush()
        return False
    