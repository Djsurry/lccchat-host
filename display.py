import os, textwrap
from colored import bg, fg, attr

def display(data):
    rows, columns = os.popen('stty size', 'r').read().split()
    header = [n for n in data.keys()][0]
    rows = int(rows) - 2
    columns = int(columns)
    right = int(columns/3)
    left = int(columns/3)
    middle = columns - (right + left)
    lines = []
    for from_me, msg in reversed(data[header]):
        if from_me:
            side = "RIGHT"
        else:
            side = "LEFT"
        l = []
        multiLine = textwrap.fill(msg, right)
        l.append(multiLine.split('\n'))
            
        val = []
        for i in l:
            for s in i:
                val.append([side, s])
        lines += val
    lines.append(["CENTER", "Texting: {}".format(header)])

    total = 0
    while len(lines) + total <= rows:
        total += 1
    
    # PRINTS BLANK LINES 
    for _ in range(total):
        print()
    for line in reversed(lines):
        if line[0] == "CENTER":
            pass
        elif line[0] == "LEFT":

            print('{0}{1}{2}{3}'.format(fg(15),bg(240),line[1],attr(0)))

        else:

            print(' '*(columns-right) + ' '*(right-len(line[1]))+ '{0}{1}{2}{3}'.format(fg(15),bg(26),line[1],attr(0)))
    # PRINTS HEADER
    print([n for n in reversed(lines)][0][1].center(columns))
            
#max out at 10000 bytes
data = {
    "dsurry@wearelcc.ca":[
        (True, "hey"),
        (False, "hey"),
        (True, "whats up"),
        (False, "nm"),
        (True, "this is a really long message im hoping to      test wrapping LOL 5head"),
        (False, "this is a really long message im hoping to     test wrapping LOL 5head")
    ]

}
if __name__ == "__main__":
    display(data)
