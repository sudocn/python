#!/usr/bin/python

def kmp1(pattern):
    next = list('a'*len(pattern))
    next[0] = -1
    j = 0
    k = -1
    while j < len(pattern) - 1:
        if k == -1 or pattern[j] == pattern[k]:
            j += 1
            k += 1
            if pattern[j] == pattern[k]:
                next[j] = next[k]
            else:
                next[j] = k
        else:
            k = next[k]

    return next

if __name__ == "__main__":
    print( kmp1("ababaa") )
    print(kmp1("abcabcd"))
    print(kmp1("abcdabce"))
    print(kmp1("abacdababc"))