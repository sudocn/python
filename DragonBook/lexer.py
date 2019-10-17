#!/usr/bin/python

import sys

class Tag(object):
    NUM = 256
    ID = 257
    TRUE = 258
    FALSE = 259

    @classmethod
    def tostring(cls, t):
        dc = {cls.NUM:"NUM", cls.ID:"ID", cls.TRUE:"TRUE", cls.FALSE:"FALSE"}
        if t in dc:
            return dc[t]
        else:
            return "{}".format(chr(t), t)

class Token(object):
    def __init__(self, t):
        if isinstance(t, str):
            t = ord(t)
        assert(isinstance(t, int))
        self.tag = t

    def __str__(self):
        return '<' + Tag.tostring(self.tag) + '>'

class Num(Token):
    def __init__(self, v):
        assert(isinstance(v, (int, float)))
        super(Num, self).__init__(Tag.NUM)
        self.value = v
    
    def __str__(self):
        return '<{},{}>'.format(Tag.tostring(self.tag), self.value)

class Word(Token):
    def __init__(self, t, s):
        assert(isinstance(s, (str, unicode)))
        super(Word, self).__init__(t)
        self.lexeme = s

    def __str__(self):
        return '<{},{}>'.format(Tag.tostring(self.tag), self.lexeme)

#
#
#

def PEEK():
    c = sys.stdin.read(1)
    if c:
        return c
    else:
        raise EOFError()

class Lexer(object):
    def __init__(self):
        self.line = 1
        self.peek = ' '
        self.words = {}
        
        self.reserve(Word(Tag.TRUE, "true"))
        self.reserve(Word(Tag.FALSE, "false"))

    def reserve(self, t):
        self.words[t.lexeme] = t

    def scan(self):
        while True:
            if self.peek in (' ', '\t'):
                pass
            elif self.peek == '\n':
                self.line += 1
            else:
                break
            self.peek = PEEK()

        if self.peek.isdigit():
            v = int(self.peek)
            self.peek = PEEK()
            while self.peek.isdigit():
                v = 10*v + int(self.peek)
                self.peek = PEEK()
            return Num(v)

        if self.peek.isalpha():
            b = [self.peek]
            self.peek = PEEK()
            while self.peek.isalnum():
                b.append(self.peek)
                self.peek = PEEK()
            s = ''.join(b)
            if s not in self.words:
                self.words[s] = Word(Tag.ID, s)
            return self.words[s]

        p = self.peek
        self.peek = ' '
        return Token(p)

def parse(stream=None):
    lex = Lexer()
    tstack = []
    if stream:
        saved_stdin = sys.stdin
        sys.stdin = stream
    try:
        while True:
            t = lex.scan()
            tstack.append(t)
    except EOFError:
        pass
    finally:
        if stream:
            sys.stdin = saved_stdin
        return ' '.join(map(str,tstack))

import unittest
class CaseLexer(unittest.TestCase):
    def test_tokens(self):
        t1 = Token('+')
        n1 = Num(12345)
        w1 = Word(Tag.TRUE, 'true')
        w2 = Word(Tag.FALSE, 'false')
        w3 = Word(Tag.ID, 'hello')

        print t1,n1,w1,w2,w3

    def test_lexer(self):
        lex = Lexer()
        print lex.words

    def test_parsefile(self):
        with open("starconv.lex") as f:
            expect = f.read().rstrip("\r\n") # remove the tailing \r or \n
        with open("starconv.c") as f:
            result = parse(f)

        self.maxDiff = None
        self.assertMultiLineEqual(result.replace(' ', '\n'), expect.replace(' ', '\n'))

if __name__ == "__main__":
    print parse()