#!/usr/bin/python

import sys

class Tag(object):
    NUM = 256
    ID = 257
    TRUE = 258
    FALSE = 259
    OP = 260

    @classmethod
    def tostring(cls, t):
        dc = {cls.NUM:"NUM", cls.ID:"ID", cls.TRUE:"TRUE", cls.FALSE:"FALSE", cls.OP:"OP"}
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

class Oper(Token):
    '''
    Operators 
    '''
    LT = 1
    LE = 2
    EQ = 3
    NE = 4
    GE = 5
    GT = 6

    volcabulary = {
        '<' : LT, 
        '<=': LE, 
        '==': EQ, 
        '!=': NE, 
        '>=': GE, 
        '>': GT}

    def __init__(self, t):
        print "oper => '{}'".format(t)
        assert(t in self.volcabulary)
        super(Oper, self).__init__(Tag.OP)
        self.type = self.volcabulary[t]
        self.repr = t
    
    def __str__(self):
        return '<{},{}>'.format(Tag.tostring(self.tag), self.repr)

#
#
#

class Source(object):
    def __init__(self, stream=sys.stdin):
        self.stream = stream
        self.reserve = ''
    
    def getc(self):
        if self.reserve:
            c = self.reserve
            self.reserve = ''
        else:
            c = self.stream.read(1)

        if not c: raise EOFError()
        return c

    def ungetc(self, c):
        if self.reserve:
            raise Exception("CAN NOT UNGET TWICE!!")
        self.reserve = c

source = None
def PEEK(): # peek actually read out the char
    return source.getc()

def UNPEEK(c):
    source.ungetc(c)

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
        # space and line ending
        while True:
            if self.peek in (' ', '\t'):
                pass
            elif self.peek == '\n':
                self.line += 1
            # comments
            elif self.peek == '/':
                nextpeek = PEEK()
                if nextpeek == '/': # //
                    skip = PEEK()
                    while skip != '\n':
                        skip = PEEK()
                    self.peek = skip
                elif nextpeek == '*': # /* ... */
                    skip = PEEK()
                    while True:
                        if skip == '*' and PEEK() == '/':
                            break
                        skip = PEEK()
                else:
                    UNPEEK(nextpeek)
                    break
            else:
                break
            self.peek = PEEK()
                
        # numbers
        #if self.peek.isdigit():
        if self.peek in '.0123456789':
            f = 1   # fraction
            v = 0
            if self.peek == '.':
                f = 10.0
            else:
                v = int(self.peek)

            self.peek = PEEK()
            while self.peek.isdigit() or (f == 1 and self.peek == '.'):
                if self.peek == '.':
                    f = 10.0
                elif f > 1:
                    v = v + int(self.peek) / f
                    f *= 10
                else:
                    v = 10*v + int(self.peek)
                
                self.peek = PEEK()
            return Num(v)

        # string tokens
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

        # operators <, <=, ==, !=, >=, >
        if self.peek in '<!=>':
            nextpeek = PEEK()
            op = self.peek
            if nextpeek == '=': # 2 char operator
                self.peek = PEEK()
                return Oper(op + '=')
            else:
                UNPEEK(nextpeek)

            if self.peek in '<>':
                self.peek = PEEK()
                return Oper(op)

        p = self.peek
        self.peek = ' '
        return Token(p)

def parse(stream=sys.stdin):
    global source
    lex = Lexer()
    tstack = []
    source = Source(stream)
    try:
        while True:
            t = lex.scan()
            tstack.append(t)
    except EOFError:
        pass

    return ' '.join(map(str,tstack))

import unittest
class CaseLexer(unittest.TestCase):
    def test_tokens(self):
        t1 = Token('+')
        n1 = Num(12345)
        w1 = Word(Tag.TRUE, 'true')
        w2 = Word(Tag.FALSE, 'false')
        w3 = Word(Tag.ID, 'hello')
        o1 = Oper('<')
        o2 = Oper('==')

        print t1,n1,w1,w2,w3,o1,o2

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