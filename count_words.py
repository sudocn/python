#!/usr/bin/python
from collections import Counter
import sys

print sys.argv
with open(sys.argv[1], "r") as f:
    wordcount = Counter(f.read().split())

    for item in wordcount.items(): 
        print("{}\t{}".format(*item))
