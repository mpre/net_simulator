'''
Created on 16/dic/2012

@author: mpre
'''

import numpy
import random

MAX_WL_HISTORY = 50
MAX_VARIANCE_VALUE = 1000

class InfoManager(object):

    def __init__(self):
        self.next_job_id = 0
        self.moved_jobs = 0
        self.new_jobs = 0
        self.ended_jobs_this_frame = 0
        self.ended_jobs = 0
        self.ended_jobs_total_move = 0
        self.cell_workload_history = {}
        self.wl_history = []
        self.moved_jobs_history = []
        self.wl_variance_history = []
        self.new_jobs_history = []
        self.medium_distance_history = []
        self.average_moved_times = []
        
    def add_cell(self, cellname, history_len=0, default_value=0):
        self.cell_workload_history[cellname] = []
        for _ in range(history_len):
            self.cell_workload_history[cellname].append(default_value)
            
    def add_cell_wl(self, cellname, wl):
        self.cell_workload_history[cellname].append(wl)
        if len(self.cell_workload_history) > MAX_WL_HISTORY:
            self.cell_workload_history.pop(0)

    def add_cell_distance(self, dist):
        self.medium_distance_history.append(dist)
        if len(self.medium_distance_history) > MAX_WL_HISTORY:
            self.medium_distance_history.pop(0)
            
    def cell_keys(self):
        return self.cell_workload_history.keys()
    
    def cell_length(self):
        return len(self.cell_workload_history[random.choice(self.cell_workload_history.keys())])
    
    def calc_frame_values(self):
        wl = [x[-1] for x in self.cell_workload_history.values()]
       
        self.wl_history.append(numpy.average(wl))
        if len(self.wl_history) > MAX_WL_HISTORY:
            self.wl_history.pop(0)
        
        self.wl_variance_history.append(numpy.var(wl))
        if len(self.wl_variance_history) > MAX_WL_HISTORY:
            self.wl_variance_history.pop(0)
        
        self.new_jobs_history.append(self.new_jobs)
        if len(self.new_jobs_history) > MAX_WL_HISTORY:
            self.new_jobs_history.pop(0)
        self.new_jobs = 0
        
        self.moved_jobs_history.append(self.moved_jobs)
        if len(self.moved_jobs_history) > MAX_WL_HISTORY:
            self.moved_jobs_history.pop(0)
        self.moved_jobs = 0
                    
        self.average_moved_times.append(float(self.ended_jobs_total_move)/(max(self.ended_jobs,1)))
        if len(self.average_moved_times) > MAX_WL_HISTORY:
            self.average_moved_times.pop(0)
        
    def get_next_jobid(self):
        self.next_job_id += 1
        self.new_jobs += 1
        return self.next_job_id
    
    def add_moved_job(self):
        self.moved_jobs += 1
    
    def add_ended_job(self, moves):
        self.ended_jobs += 1
        self.ended_jobs_this_frame += 1
        self.ended_jobs_total_move += moves
        
        
info_mgr = InfoManager()