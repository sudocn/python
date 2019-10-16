#!/usr/bin/python


KEYWORDS  = list('0123456789')
PUNCTURES = ['+', '-']  # used by scanner to split tokens

class ParseError(Exception):
    pass

def report(msg):
    raise ParseError(msg)

class Scanner(object): 
    '''
    Linear analysis
    lexical analysis / scanning
    '''

    class Line(object):
        '''
        One line, can peek ahead one char
        '''
        def __init(self, string):
            self.content = string
            self.index = 0

        def get(self):
            if self.index < len(self.content):
                self.index += 1
                return self.content[self.index - 1]
            else:
                return ''

        def peek(self):
            if self.index + 1 < len(self.content):
                return self.content[self.index + 1]
            else:
                return ''

    def __init__(self, src):
        self.dish = ''
        self.scanning(src)
        
    def feed(self, c):
        if c.isspace():
            self.swallow()
        elif c in PUNCTURES:
            self.swallow()
            self.dish = c
            self.swallow()
        else:
            self.dish += c

    def swallow(self):
        if self.dish: 
            self.tokens.append(self.dish)
            self.dish = ''

    def scanning(self, src):
        self.tokens = []
        self.dish = ''
        for c in src:
            self.feed(c)
    
        # end scanning
        self.swallow()

    def scanfile(self, fname):
        self.tokens = []
        self.dish = ''
        with open(fname) as f:
            for line in f:

#############################################################
class Parser(object):
    '''
    Hierarchical analysis
    syntax analysis / parsing
    '''
    terminals = KEYWORDS + PUNCTURES
    def __init__(self, tokens):
        #self.cur = 0
        self.ahead = 0
        self.tokens = tokens

    def current(self):
        return self.tokens[self.cur]

    def lookahead(self):
        if self.ahead < len(self.tokens):
            return self.tokens[self.ahead]

    def next_terminal(self):
        for i in range(self.ahead + 1, len(self.tokens)):
            if self.tokens[i] in self.terminals:
                self.ahead = i
                break

    def stmt(self):
        la = self.lookahead()
        print("stmt: lookahead = {}".format(la))
        if la == "expr":
            self.match('expr', ';')
        elif la == "if":
            self.match('if', '(', 'expr', ')')
            self.stmt()
        elif la == "for":
            self.match('for', '(')
            self.optexpr()
            self.match(';')
            self.optexpr()
            self.match(';')
            self.optexpr()
            self.match(')')
            self.stmt()
        elif la == "other":
            self.match('other')
        else:
            report("syntax error 1")

    def optexpr(self):
        if (self.lookahead() == "expr"):
            self.match("expr")

    def match_one(self, terminal):
        if (self.lookahead() == terminal):
            self.next_terminal()
        else:
            report("syntax error 2 {}".format(terminal))
            report('match: {}, lookahead = {}'.format(terminal, self.lookahead()))

    def match(self, *terminal_list):
        for t in terminal_list:
            self.match_one(t)

class Parser253(Parser):

    def expr(self):
        self.term()
        self.rest()
    
    def rest(self):
        while True:
            la = self.lookahead()
            if la == '+':
                self.match('+')
                self.term()
                print('+')
                #self.rest()
            elif la == '-':
                self.match('-')
                self.term()
                print('-')
                #self.rest()
            else:
                break

    def term(self):
        la = self.lookahead()
        print("term: lookahead = {}".format(la))

        if la in '0123456789':
            self.match(la)
            print(la)
        else:
            report('syntax error 3')
            
if __name__ == '__main__':
    #source = 'for ( ; expr ; expr ) other'
    source = '9-5+2'
    lex = Scanner(source)
    print(lex.tokens)
    par = Parser253(lex.tokens)
    par.expr()