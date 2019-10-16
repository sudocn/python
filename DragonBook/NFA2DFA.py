#!/usr/bin/python
import yaml
from graphviz import Digraph 

trans = \
'''
0:
    a: [0,1]
    b: [0]
1:
    b: [2]
2:
    b: [3]
3:
'''

def draw(table, start, accept):
    '''
    Draw a NFA graph by transition table
    table: transition table
    start: start state
    accept: accepting states
    '''
    g = Digraph('NFA', filename='NFA.gv',
    node_attr={'shape':'circle'},
    edge_attr={'arrowhead':'normal'})

    # create states
    for state in table.keys():
        if state in accept:
            g.node(str(state),  shape='doublecircle')
        else:
            g.node(str(state))

    # add start arrow
    g.node('start', shape='none')
    g.edge('start', str(start))

    # add tranistions
    #g.edges(['01', '12', '14', '23', '45', '36', '56', '67'])
    for src, trans in table.items():
        if trans is None: continue
        for alpha, dest_list in trans.items():
            for dest in dest_list:
                print "adding {} -{}-> {}".format(src, alpha, dest)
                g.edge(str(src), str(dest), str(alpha)) 

    #g.edge('0', '7', 'E', constraint='false')
    #g.edge('6', '1', 'E', constraint='false')

    # draw 
    g.view()


y = yaml.load(trans)
print yaml.dump(y)
print y.keys()
draw(y, 0, [3])
    