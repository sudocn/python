#!/usr/bin/python

import sys

def hex2string(hex_string):
    if len(hex_string) % 2 == 1:
        hex_string = '0' + hex_string

    while len(hex_string) > 0:
        char,hex_string = hex_string[:2], hex_string[2:]
        print chr(int(char, 16)),

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: " + sys.argv[0] + " hex_stirng"
    else:
        hex2string(sys.argv[1])
