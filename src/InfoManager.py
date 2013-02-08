'''
Created on 16/dic/2012

@author: mpre
'''

import numpy
import random
from LogManager import msg_mgr

MAX_WL_HISTORY = 50
MAX_VARIANCE_VALUE = 1000

WL_HIST_FN = "data/wl.csv"
WL_VAR_HIST_FN = "data/wl_var.csv"
AVG_DIST_FN = "data/avg_dist.csv"
AVG_MOVED_TIMES_FN = "data/avg_moves.csv"
MOVED_JOBS_FN = "data/mvd_jobs.csv"
LOST_JOBS_FN = "data/lost_jobs.csv"

def position_name(node):
    return "{0}{1}".format(*node.position)

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
        self.lost_jobs = 0
        self.lost_jobs_h = []
        self.switches = {}
        
        self.wl_fout = open(WL_HIST_FN, 'w')
        self.wl_var_fout = open(WL_VAR_HIST_FN, 'w')
        self.avg_dist_fout = open(AVG_DIST_FN, 'w')
        self.avg_move_fout = open(AVG_MOVED_TIMES_FN, 'w')
        self.mvd_jobs_fout = open(MOVED_JOBS_FN, 'w')
        self.lost_jobs_fout = open(LOST_JOBS_FN, 'w')
        
    def add_cell(self, cellname, history_len=0, default_value=0):
        self.cell_workload_history[cellname] = []
        for _ in range(history_len):
            self.cell_workload_history[cellname].append(default_value)
            
    def remove_cell(self, cellname):
        del self.cell_workload_history[cellname]
            
    def add_cell_wl(self, cellname, wl):
        self.cell_workload_history[cellname].append(wl)
        if len(self.cell_workload_history[cellname]) > MAX_WL_HISTORY:
            self.cell_workload_history[cellname].pop(0)

    def add_cell_distance(self, dist):
        self.medium_distance_history.append(dist)
        if len(self.medium_distance_history) > MAX_WL_HISTORY:
            self.avg_dist_fout.write("{0}\n".format(str(self.medium_distance_history.pop(0))))
            
    def cell_keys(self):
        return self.cell_workload_history.keys()
    
    def cell_length(self):
        if self.cell_workload_history:
            return len(self.cell_workload_history[random.choice(self.cell_workload_history.keys())])
        else:
            return 0
    
    def add_switch(self, cell_one, cell_two):
        cell_one_name = position_name(cell_one)
        cell_two_name = position_name(cell_two)
        if cell_one_name not in self.switches:
            color = [random.randint(0,255), random.randint(0,255), random.randint(0,255)]
            self.switches[cell_one_name] = (cell_one, color)
            self.switches[cell_two_name] = (cell_two, color)
            
    def remove_switch(self, cell):
        cell_name = position_name(cell)
        if cell_name in self.switches:
            del self.switches[cell_name]
        else:
            msg_mgr.add_msg("[ERROR] Can't remove switch of {0}".format(cell_name))
              
    def calc_frame_values(self):
        wl = [x[-1] for x in self.cell_workload_history.values()]
       
        self.wl_history.append(numpy.average(wl))
        if len(self.wl_history) > MAX_WL_HISTORY:
            self.wl_fout.write("{0}\n".format(str(self.wl_history.pop(0))))
        
        self.wl_variance_history.append(numpy.sqrt(numpy.var(wl)))
        if len(self.wl_variance_history) > MAX_WL_HISTORY:
            self.wl_var_fout.write("{0}\n".format(str(self.wl_variance_history.pop(0))))        
            
        self.new_jobs_history.append(self.new_jobs)
        if len(self.new_jobs_history) > MAX_WL_HISTORY:
            self.new_jobs_history.pop(0)
        self.new_jobs = 0
        
        self.lost_jobs_h.append(self.lost_jobs)
        if len(self.lost_jobs_h) > MAX_WL_HISTORY:
            self.lost_jobs_fout.write("{0}\n".format(self.lost_jobs_h.pop(0)))
        
        self.moved_jobs_history.append(self.moved_jobs)
        if len(self.moved_jobs_history) > MAX_WL_HISTORY:
            self.mvd_jobs_fout.write("{0}\n".format(str(self.moved_jobs_history.pop(0))))
        self.moved_jobs = 0
                    
        self.average_moved_times.append(float(self.ended_jobs_total_move)/(max(self.ended_jobs,1)))
        if len(self.average_moved_times) > MAX_WL_HISTORY:
            self.avg_move_fout.write("{0}\n".format(str(self.average_moved_times.pop(0))))
        
    def get_next_jobid(self):
        self.next_job_id += 1
        self.new_jobs += 1
        return self.next_job_id
    
    def add_moved_job(self):
        self.moved_jobs += 1
    
    def add_lost_job(self, n):
        self.lost_jobs += n
    
    def add_ended_job(self, moves):
        self.ended_jobs += 1
        self.ended_jobs_this_frame += 1
        self.ended_jobs_total_move += moves
        
    def finalize_stats(self):
        for x in self.wl_history:
            self.wl_fout.write("{0}\n".format(str(x)))            
        self.wl_fout.close()
        
        for x in self.wl_variance_history:
            self.wl_var_fout.write("{0}\n".format(str(x)))
        self.wl_var_fout.close()
        
        for x in self.medium_distance_history:
            self.avg_dist_fout.write("{0}\n".format(str(x)))
        self.avg_dist_fout.close()
        
        for x in self.average_moved_times:
            self.avg_move_fout.write("{0}\n".format(str(x)))
        self.avg_move_fout.close()
        
        for x in self.moved_jobs_history:
            self.mvd_jobs_fout.write("{0}\n".format(str(x)))
        self.mvd_jobs_fout.close()
        
        for x in self.lost_jobs_h:
            self.lost_jobs_fout.write("{0}\n".format(str(x)))
        self.lost_jobs_fout.close()
        return
        
        
info_mgr = InfoManager()