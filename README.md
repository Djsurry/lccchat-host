# A message to those looking for vulnerabilities
First of all, thank you! I know this code is a mess and I'm sorry. I have no professional experience and just survive off
google and stack overflow. I will give a general run-down of what the app does. Also note that it obviously isn't in its
final form. All that is done is the networking, authentication and crypto. Ok here it goes


This is split up into two repos, this one and [LccChat](https://github.com/Djsurry/lccchat). The later is the website, and
handles verification of emails. 


The way this works is the `basicserver.py` file is run on the server with root privelages, and then a user runs `/cli/host.py`.
They both reference other files in the repo, and <b>there are a lot of junk files</b>. If it isnt imported by either of those
two files it probably isn't very important.

## Abstraction
So pretty much the user generates a RSA key and sends it and their email to the server, plaintext. The server then sends a 
verificationlink to that email. Once verified, the user restarts the program. The RSA key from earlier and email are sent once 
more, plaintext, and the server response with an AES key encrypted with the public key. The user them decrypts it with their
private key. Now communication happens with that AES keys

##THANK YOU
