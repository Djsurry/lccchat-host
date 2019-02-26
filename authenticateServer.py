
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
        write("MAKING NEW ENTRY")
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
        write(213123123123121)
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
    write("1")

    pubkey = host.socket.read(blocking=True)
    write('2')

    # if not email or not pubkey:
    #     sys.stdout.write("EMAIL OR PUBKEY NOT SENT")
    #     return False
    
    a = [n for n in c.execute("select email from users where email=?", (hash_string(email),))]
    write('3')


    if not a:
        write('here')
        sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
        host.socket.send("ERR VERIFY {}".format(email))
        write("NOT ON RECORD")
        return False
    write(str([n for n in c.execute("select pubkey, verified from users where email=?", (hash_string(email),))][0]))
    r = [n for n in c.execute("select pubkey, verified from users where email=?", (hash_string(email),))][0]
    write(f"r1: {r}")
    write('5')
    p = [n for n in r[0].split(":") if n]
    write('6')
    write(f"r1: {r[1]}")
    write(f"p: {p}")

    a = [int(n) for n in r[1].split()]

    write('7')

    if pubkey in p:
        write("ASDAS")
        write(f"a: {a}")
        write(f"index: {p.index(pubkey)}")


        if a[p.index(pubkey)] == 0:
            write("VERIFY NEEDED")

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

            return key, email
    
    else:
        write("3123")

        sendEmail(email, "Verify", "Click here: {}".format(verify(email, pubkey)))
        host.socket.send("ERR VERIFY {}".format(email))
        write("PUBKEY NOT IN LISTED PUBKEYS")

        return False
    