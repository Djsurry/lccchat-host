from typing import List
def main(l: List[List[str]]) -> int:
    for i in l:
        print([n for n in i])
    return 2

main([['hi', 'bye'], ['you', 'are', 'cool'], ['foo', 'bar']])
