'''
Created on 10/dic/2012

@author: mpre
'''

import math
import numpy

from LogManager import msg_mgr
from InfoManager import info_mgr

L = 'LEFT'
R = 'RIGHT'
U = 'UP'
D = 'DOWN'

MAX_CELLS = 16

MOVE_COOLDOWN = 500

class ca_cell(object):
    
    def __init__(self, position=None, element=None, neighbor=None):
        self.position = position
        self.neighbor = {} # keys = {'UP', 'DOWN', 'RIGHT', 'LEFT'}
        self.neighbor[U] = None
        self.neighbor[D] = None
        self.neighbor[R] = None
        self.neighbor[L] = None
        self.element = element
        self.element.cell = self
        self.net = None
        
    def add_neighbor(self, cell):
        # print "ADD NEIGH > ", str(self.position), str(cell.position)
        if cell.position == (self.position[0] -1, self.position[1]):
            self.neighbor[L] = cell
            cell.neighbor[R] = self
        elif cell.position == (self.position[0], self.position[1] -1):
            self.neighbor[U] = cell
            cell.neighbor[D] = self
        elif cell.position == (self.position[0] +1, self.position[1]):
            self.neighbor[R] = cell
            cell.neighbor[L] = self
        elif cell.position == (self.position[0], self.position[1] +1):
            self.neighbor[D] = cell
            cell.neighbor[U] = self
        else:
            msg_mgr.add_msg("[ERROR] : ca.py > add_neighbor. SELF = {0} : OTHER = {1}".format(self, cell))
    
    def switch_with(self, cell):
        temp = self.element
        self.element = cell.element
        self.element.cell = self
        cell.element = temp
        cell.element.cell = cell 
        self.element.already_moved = MOVE_COOLDOWN
        cell.element.already_moved = MOVE_COOLDOWN
        msg_mgr.add_msg("[INFO] Switched elements between {0} and {1}".format(self, cell))
        info_mgr.add_switch(self, cell)
        
    def set_net(self, net):
        self.net = net
           
    def __str__(self):
        return "{0}".format(self.position)
    

class ca_net(object):
    
    def __init__(self):
        self.limit = 0
        self.next_new = [0,0]
        self.add_direction = U
        self.elements = {}
       
    def full(self):
        return len(self.elements) == MAX_CELLS    
    
    def get_node_geo_pos(self, position):
        r = None
        for e in self.elements:
            if position_name(e.element.position) == position:
                r = None
        return r

    def elements_position(self):
        return [self.elements[cell].element.position for cell in self.elements]
        
    def add_element(self, element):
        # print self.limit, MAX_CELLS
        if 2*(self.limit+1) > math.sqrt(MAX_CELLS):
            msg_mgr.add_msg("[INFO] > Too many cells, pass")
            return False
        position = "{0}-{1}".format(self.next_new[0], self.next_new[1])
        pos_vector = (self.next_new[0], self.next_new[1])
        if not position in self.elements:
            element.position = (pos_vector[0], pos_vector[1])
            self.elements[position] = element
            self.elements[position].set_net(self)
            for p in ((pos_vector[0], pos_vector[1]-1),
                      (pos_vector[0], pos_vector[1]+1),
                      (pos_vector[0]-1, pos_vector[1]),
                      (pos_vector[0]+1, pos_vector[1])):
                neig_pos = "{0}-{1}".format(p[0], p[1])
                if neig_pos in self.elements:
                    self.elements[neig_pos].add_neighbor(element)
            if self.add_direction == U:
                self.next_new = (self.next_new[0], self.next_new[1] -1)
                if self.next_new[1] < -self.limit:
                    self.add_direction = R
            elif self.add_direction == R:
                self.next_new = (self.next_new[0] +1, self.next_new[1])
                if self.next_new[0] > self.limit:
                    self.add_direction = D 
            elif self.add_direction == D:
                self.next_new = (self.next_new[0], self.next_new[1] +1)
                if self.next_new[1] > self.limit:
                    self.add_direction = L
            else:
                self.next_new = (self.next_new[0] -1, self.next_new[1])
                if self.next_new[0] < -self.limit:
                    self.add_direction = U
            return pos_vector
        else:
            self.limit += 1
            self.next_new = (self.next_new[0]-1, self.next_new[1] -1)
            return self.add_element(element)
            
    def update(self, millisec):
        for e in self.elements:
            self.elements[e].element.calculate_workload(millisec)
        for e in self.elements:
            self.elements[e].element.update(millisec)           
        return
    
    def calc_geo_distance(self):
        dist = []
        for e in self.elements:
            el_dists = []
            pos = self.elements[e].element.position
            for neigh in self.elements[e].neighbor:
                if self.elements[e].neighbor[neigh]:
                    neigh_pos = self.elements[e].neighbor[neigh].element.position
                    el_dists.append(math.sqrt((pos[0] - neigh_pos[0])**2 + (pos[1] - neigh_pos[1])**2))
            dist.append(numpy.average(el_dists))
        return numpy.average(dist)
                
    def __str__(self):
        s = ""
        for i in range(-self.limit-1, self.limit+2):
            for j in range(-self.limit-1, self.limit+2):
                position = "{0}-{1}".format(j, i)
                if position in self.elements:
                    s += "{0:^5}".format(self.elements[position].element.position)
                else:
                    s += " - "
            s+= "\n"
        return s
                    
    pass


















