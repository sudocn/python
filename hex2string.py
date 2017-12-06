#!/usr/bin/python

import sys

def hex2string(hex_string):
    output=''
    if len(hex_string) % 2 == 1:
        hex_string = '0' + hex_string

    while len(hex_string) > 0:
        char,hex_string = hex_string[:2], hex_string[2:]
        output += chr(int(char, 16))
    return output

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: " + sys.argv[0] + " hex_stirng"
    elif len(sys.argv) == 2:
        print hex2string(sys.argv[1])
    else:
        msg = ''
        for word in sys.argv[1:]:
            if len(word) != 8:
                raise Exception("words must be 32 bits (8 hex numbers)")
            wstr = hex2string(word)[::-1]
            msg +=wstr
        print msg