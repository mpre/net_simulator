'''
Created on 10/dic/2012

@author: mpre
'''

import random
import math
import numpy

from LogManager import msg_mgr
from InfoManager import info_mgr

from misc import position_name

WL_DEACTIVATE_THRESHOLD = 0.3
WL_ACTIVATE_THRESHOLD = 0.3
WL_PERCENTAGE_TOLERATION = 0.95

MAX_MOVING_TRIES_FAIL = 20
JOB_MILLISEC_COOLDOWN = 50

MOVING_P = 0.4

DISABLE_COMMUNICATIONS = False
DISABLE_JUMP_COMMUNICATIONS = False

def euclidean_dist(x, y):
    return math.sqrt((x.position[0] - y.position[0])**2 + 
                     (x.position[1] - y.position[1])**2)

class job(object):
    
    def __init__(self, identifier, start_time, work_requested, minimum_workload=1.0, end_request = None):
        self.id = identifier
        self.start_time = start_time
        self.work_requested = float(work_requested)
        self.end_request = end_request
        self.minimum_workload = minimum_workload
        self.end = False
        self.moved_times = 0
        self.cooldown = 0
        
    def set_moved(self):
        self.moved_times += 1
        self.cooldown = JOB_MILLISEC_COOLDOWN
        
    def will_move(self):
        if self.cooldown <= 0 and random.random() < 1.0/(1.0+float(self.moved_times)) + 0.05:
            return True
        return False
        
    def update(self, milliseconds):
        if self.cooldown > 0:
            self.cooldown -= milliseconds
        else:
            self.work_requested -= milliseconds
        if self.work_requested <= 0:
            self.end = True
            msg_mgr.add_msg("[INFO] JOB {0} ENDED".format(self.id))

class node(object):
    
    def __init__(self, position = (0, 0), cell=None, max_workload = 100.0):
        self.cell = cell
        self.position = position
        self.max_workload = float(max_workload)
        self.current_workload = 0.0
        self.jobs = {}
        self.communicate = False
        self.already_moved = 0
    
    
    def remove(self):
        #self.cell.remove()
        self.max_workload = 0
        self.current_workload = 0
        print self.jobs
        print len(self.jobs)
        info_mgr.add_lost_job(len(self.jobs))
        info_mgr.remove_cell(position_name(self))
        self.position = None
        self.jobs = {}
        self.already_moved = 0
        self = None
    
    def add_job(self, job):
        self.jobs[job.id] = job
    
    @property
    def workload(self):
        return self.current_workload
    
    def calculate_workload(self, millisec):
        wl = 0.0
        for jk in self.jobs:
            job = self.jobs[jk]
            if job.end_request:
                wl += (job.work_requested * float((millisec - job.start_time)) / float((job.end_request - job.start_time)))
            else:
                wl += job.minimum_workload
        self.current_workload = wl
        
        
    def calc_neigh_workload(self, neigh_vector):
        wl = 0.0
        if neigh_vector:
            for n in neigh_vector:
                wl += n.element.current_workload/(n.element.max_workload*len(neigh_vector))
            return wl
        return 1.0
        
    def update(self, millisec):
                
        neighbor_in_help = []
        
        if self.current_workload/self.max_workload < WL_DEACTIVATE_THRESHOLD:
            self.communicate = False  
        elif self.current_workload/self.max_workload > WL_ACTIVATE_THRESHOLD:
            self.communicate = True
            # print self.cell.position, " has too many jobs"
        
        if self.already_moved >0:
            self.already_moved -=millisec
            if self.already_moved <=0:
                info_mgr.remove_switch(self.cell)
        
        elif (not DISABLE_JUMP_COMMUNICATIONS) and (not DISABLE_COMMUNICATIONS) and random.random() < MOVING_P and self.already_moved <=0:
            # chose a random element of the net
            possible_cells = [x for x in self.cell.net.elements.values() if x != self.cell and x.element.already_moved <= 0]
            if possible_cells:
                print possible_cells
                other_cell = random.choice(possible_cells)
                                   
                dist_self_here = []
                for cell_neigh in self.cell.neighbor.values():
                    if cell_neigh:
                        d = euclidean_dist(self, cell_neigh.element)
                        dist_self_here.append(d)
                dist_self_there = []
                for cell_neigh in other_cell.neighbor.values():
                    if cell_neigh:
                        if cell_neigh.position != self.cell.position:
                            d = euclidean_dist(self, cell_neigh.element)
                        else:
                            d = euclidean_dist(self, other_cell.element)
                        dist_self_there.append(d)

    
                dist_other_here = []
                for cell_neigh in self.cell.neighbor.values():
                    if cell_neigh:
                        if cell_neigh.position != other_cell.position:
                            d = euclidean_dist(other_cell.element, cell_neigh.element)
                        else:
                            d = euclidean_dist(other_cell.element, self)
                        dist_other_here.append(d)
                dist_other_there = []
                for cell_neigh in other_cell.neighbor.values():
                    if cell_neigh:
                        d = euclidean_dist(other_cell.element, cell_neigh.element)
                        dist_other_there.append(d)
                        
                if len(dist_self_here) > 0 and len(dist_self_there) > 0 and len(dist_other_here) > 0 and len(dist_other_there) > 0:
#                    print self.position, other_cell.element.position, numpy.average(dist_self_here), numpy.average(dist_self_there)
                    if numpy.average(dist_self_there + dist_other_here) < numpy.average(dist_self_here + dist_other_there):
                        self.cell.switch_with(other_cell)
                    else:
                        neighbor_in_help.append(other_cell)
#                    elif min(dist_self_there) == min(dist_self_here):
#                        if len(dist_self_there) > len(dist_self_here):
#                            if numpy.average(dist_other_here) < numpy.average(dist_other_there):
#                                self.cell.switch_with(other_cell)


        
        if (not DISABLE_COMMUNICATIONS) and self.communicate:
            # print "and want to communicate", self.cell.neighbor
            for n in self.cell.neighbor:
                cell_n = self.cell.neighbor[n]
                if cell_n:
                    if cell_n.element.current_workload/cell_n.element.max_workload < self.current_workload/self.max_workload:
                        neighbor_in_help.append(cell_n)
            c = ""
            for e in neighbor_in_help:
                c+= "({0},{1})\t".format(e.position[0], e.position[1])
            # print "he communicate with ",c
            if neighbor_in_help:
                medium_workload_neigh = self.calc_neigh_workload(neighbor_in_help)
                moving_tries = MAX_MOVING_TRIES_FAIL
                if medium_workload_neigh < self.current_workload/self.max_workload:
                    while self.calc_neigh_workload(neighbor_in_help) < WL_PERCENTAGE_TOLERATION*(self.current_workload/self.max_workload) and moving_tries>0:
                        for n in neighbor_in_help:
                            if self.jobs:
                                try:
                                    job_to_move = random.choice(self.jobs.keys())
                                    if self.jobs[job_to_move].will_move():
                                        msg_mgr.add_msg("[INFO] JOB {0} moved {1} times".format(self.jobs[job_to_move].id, 
                                                                                             self.jobs[job_to_move].moved_times+1))
                                        self.jobs[job_to_move].set_moved()
                                        n.element.add_job(self.jobs[job_to_move])
                                        del self.jobs[job_to_move]
                                        n.element.calculate_workload(millisec)
                                        info_mgr.add_moved_job()
                                    else:
                                        moving_tries -= 1 
                                except Exception as e:
                                    print self.jobs, len(self.jobs)
                                    msg_mgr.add_msg("[ERROR] random choice on self.jobs : {0}".format(e))
                                    moving_tries -= 1           
#                                moved_jobs += 1
#                                
#                                key_to_remove = random.choice(self.jobs.keys())
#                                n.element.add_job(self.jobs[key_to_remove])
#                                del self.jobs[key_to_remove]
#                                n.element.calculate_workload(millisec)
                        self.calculate_workload(millisec)
                        medium_workload_neigh = self.calc_neigh_workload(neighbor_in_help)
                for n in neighbor_in_help:
                    n.element.calculate_workload(millisec)
        perc_work = 1.0
        continue_jobs = {}
        ended_jobs = {}
        
        if self.current_workload > self.max_workload:
            perc_work = self.max_workload / self.current_workload
        for jk in self.jobs:
            job = self.jobs[jk]
            if job.end_request:
                job.update(perc_work * job.work_requested * float((millisec - job.start_time)) / float((job.end_request - job.start_time)))
            else:
                job.update(job.minimum_workload * perc_work)
            if job.end:
                ended_jobs[job.id] = job
                info_mgr.add_ended_job(job.moved_times)
            else:
                continue_jobs[job.id] = job
        self.jobs = continue_jobs
                
        return
        

class net(object):
    
    pass