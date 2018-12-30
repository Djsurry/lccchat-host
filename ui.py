from typing import List, Tuple, Dict
from colored import bg, fg, attr
import select
import threading
import sys, tty, termios
keys: Dict = {"ESC": '\x1b', "ENTER": '\r'}


class Updater(threading.Thread):
    def __init__(self, target, user):
        super(Updater, self).__init__()
        self.target = target
        self.data = ''
        self.user = user
    def update(self):
        self.user.send()
    def
def getch() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def chat_input(prompt: str = '') -> str:
    sys.stdout.write(prompt)
    sys.stdout.flush()
    first: str = getch()
    if first in keys.values():
        return first
    entered: List = [first]
    sys.stdout.write(first)
    sys.stdout.flush()
    while True:
        ch = getch()
        if ch == keys['ENTER']:
            sys.stdout.write('\n')
            sys.stdout.flush()
            return ''.join(entered)
        elif ch == keys['ESC']:
            sys.stdout.write('\n')
            sys.stdout.flush()
            return ch
        else:
            entered.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()


def cprint(string: str, fg: str = '', bg: str = '', attr: str = attr("reset")) -> None:
    print(fg + bg + string + attr)


def print_chat(data: List[Tuple[bool, str]], target: str) -> str:
    for entry in data:  # type: tuple
        if entry[0] == True:
            cprint(entry[1], fg=fg(33))
        else:
            cprint(entry[1], fg=fg(256))
    resp: str = chat_input(prompt="Chat with {} -> ".format(target))
    return resp


def menu() -> str:
    while True:
        print("Who would you like to text?")
        target: str = input("-> ")
        if "@wearelcc.ca" not in target:
            print("Please enter a valid LCC email")
        else:
            break
    data: List[Tuple[bool, str]] = get_data(target, MAX=1000)
    chat_loop(data, target)


def chat_loop(data: List[Tuple[bool, str]], target: str) -> None:
    inp = print_chat(data, target)
    if inp == keys['ESC']:
        return
    else:
        send(inp)

