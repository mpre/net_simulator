'''
Created on 13/dic/2012

@author: mpre
'''

MAX_MSG = 5

class LogManager(object):

    def __init__(self):
        self.msgs = []
        
    def add_msg(self, msg):
        self.msgs.append(msg)
        if len(self.msgs) > MAX_MSG:
            self.msgs.pop(0)

msg_mgr = LogManager()