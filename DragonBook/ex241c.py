#!/usr/bin/python


KEYWORDS  = ['0', '1']
PUNCTURES = ['']

def report(msg):
    print(msg)

class Scanner(object): 
    '''
    Linear analysis
    lexical analysis / scanning
    '''
    def __init__(self, src):
        self.scanning(src)
        
    def scanning(self, src):
        self.tokens = []
        t = ''
        for c in src:
            if c.isspace():
                if t: self.tokens.append(t)
                t = ''
            elif c in PUNCTURES:
                if t: self.tokens.append(t)
                t = ''
                self.tokens.append(c)
            else:
                t += c
    
        if t: self.tokens.append(t)

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
        if self.ahead + 1 == len(self.tokens):
            raise Exception("no next terminal any more")

        for i in range(self.ahead + 1, len(self.tokens)):
            print "next terminal: {}".format(i)
            if self.tokens[i] in self.terminals:
                self.ahead = i
                print "return {}".format(i)
                break

    def stmt(self):
        la = self.lookahead()
        report("stmt: lookahead = {}, ahead id {}".format(la, self.ahead))
        if la == "0":
            self.match('0')
            self.stmt()
            self.match('1')
        elif la == '1' and self.tokens[self.ahead -1] == '0':
            #self.ahead -= 1
            return
        else:
            report("syntax error 1: lookahead = {}".format(la))

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

if __name__ == '__main__':
    source = '0  1'
    lex = Scanner(source)
    print(lex.tokens)
    par = Parser(lex.tokens)
    par.stmt()