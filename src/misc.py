'''
Created on 03/feb/2013

@author: mpre
'''

def position_name(node):
    return "{0}{1}".format(*node.position)


def position_name2(position):
    return "{0}-{1}".format(*position)