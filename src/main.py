from tarfile import grp
try:
    import sys
    import pygame
    from pygame.locals import *
    import ca
    import real_net
    import random
    import matplotlib
    matplotlib.use("GTKAgg")
    import matplotlib.pyplot as plt
    import matplotlib.backends.backend_agg as agg
    from LogManager import msg_mgr
    from InfoManager import info_mgr
    from InfoManager import MAX_VARIANCE_VALUE
    from InfoManager import MAX_WL_HISTORY
    import pylab
    import numpy
    import math
except Exception, message:
    print "[ERROR] :main.py > ", message
    sys.exit(-1)
       
SQUARE_DIM = 50
CELL_PADDING = 10
AUTOMATA_OFFSET_X =  SQUARE_DIM * (math.sqrt(ca.MAX_CELLS)/2) + SQUARE_DIM/2
AUTOMATA_OFFSET_Y = (SQUARE_DIM + 10) * int(math.sqrt(ca.MAX_CELLS)/2) + 30
GEO_OFFSET_X = AUTOMATA_OFFSET_X + ((SQUARE_DIM) * int(math.sqrt(ca.MAX_CELLS) + 2)) + SQUARE_DIM
GEO_OFFSET_Y = AUTOMATA_OFFSET_Y

WINDOW_SIZE = ((SQUARE_DIM + CELL_PADDING + 5) * int(math.sqrt(ca.MAX_CELLS) * 2) + 100 + SQUARE_DIM, 
               (SQUARE_DIM + CELL_PADDING + 5) * int(math.sqrt(ca.MAX_CELLS) + 2) + 100)

LOG_OFFSET_Y = WINDOW_SIZE[1] - 80
LOG_OFFSET_X = 10

MSG_DIM = 10

TIME_SPEED = 1
MAX_FRAMERATE = 48 
C_INTERVAL = 5
GRID_FRAC = 1

## CMDS
ADD_JOB = 'a'
ADD_NODE = 'q'

def random2dpos():
    x = int(round(math.sqrt(ca.MAX_CELLS)/2))
#    print range(-x, x)
#    print (2*x)**2
    if (2*x)**2 == ca.MAX_CELLS:
        return (random.choice(range(-x, x)),
                random.choice(range(-x, x)))
    else:
        return (random.choice(range(-x+1, x)),
                random.choice(range(-x+1, x)))
    
def position_name(node):
    return "{0}{1}".format(*node.position)
    
def analyze_cmd(cmd):
    cstr = cmd[0]
    cmd = cmd[2:]
    
    params = cmd.split(',')
            
    return cstr, params
    
def main():   
    
    end = False 
    visualize_graphs = True
    
    automata = ca.ca_net() 
    
    pygame.init()
    
    plt.ion()
    
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(WINDOW_SIZE)    
    
    cmd_str = ""
    
    cmd_vect = []
    
    cmd_file = open("cmd.txt")
    for line in cmd_file.readlines():
        time, cmd = line.split(" ")
        print cmd
        cmd_vect.append([time, cmd])
    cmd_file.close()
        
    
    plt.figure(figsize=(4, 8))
#    ax1 = wl_fig.add_subplot(411)
#    ax2 = wl_fig.add_subplot(412)
#    ax3 = wl_fig.add_subplot(413)
#    ax4 = wl_fig.add_subplot(414)
    
    start_time = pygame.time.get_ticks()
    
#    jobid = 0      
#    new_jobs = 0
#    moved_jobs = 0
    
#    ended_jobs = 0
#    tot_ended_jobs = 0
#    move_of_ended_jobs = 0
#    
#    cell_wl_history = {}

#    wl_history = []
#    moved_jobs_history = []
#    wl_variance_history = []
#    new_jobs_history = []
#    medium_distance_history = []
#    average_moved_times = []
    
    activate_line = [real_net.WL_ACTIVATE_THRESHOLD*100 for _ in range(MAX_WL_HISTORY)]
    deactivate_line = [real_net.WL_DEACTIVATE_THRESHOLD*100 for _ in range(MAX_WL_HISTORY)]
    
    for _ in range(1):
        net_node = real_net.node(random2dpos())
        cell = ca.ca_cell(element = net_node)
        automata.add_element(cell)
    
    for cell in automata.elements.values():
        info_mgr.add_cell(position_name(cell.element), history_len=0)
#        cell_wl_history[position_name(cell.element)] = []
    
#    for cell in automata.elements:
#        for _ in range(random.randint(10,60)):
#            j = real_net.job(jobid, start_time, random.randint(5, 2200))
#            automata.elements[cell].element.add_job(j)
#            jobid += 1
#            new_jobs += 1
    
    i = -1
    
    font = pygame.font.Font("font.otf", 12)
    small_font = pygame.font.Font("font.otf", 8)
        
    while not end:
        clock.tick(MAX_FRAMERATE)
        i += 1
        current_time = pygame.time.get_ticks() * TIME_SPEED
        if len(cmd_vect) >= 1 and int(cmd_vect[0][0]) < current_time:
            _, cmd_str = cmd_vect.pop(0)
            msg_mgr.add_msg("[INFO] Cmd from file : {0}".format(cmd_str[:-1]))
            pygame.event.post(pygame.event.Event(USEREVENT, {'data' : cmd}))
        
        for e in pygame.event.get():
            if e.type == QUIT:
                end = True   
            elif e.type == KEYDOWN and e.key == K_n:
#                print len(automata.elements), automata.full()
                if not automata.full():
                    position = random2dpos()
                    inserted = False
                    while not inserted and not automata.full():
                        if not (position in automata.elements_position()):
                            net_node = real_net.node(position)
                            cell = ca.ca_cell(element = net_node)
                            if automata.add_element(cell):
                                info_mgr.add_cell(position_name(net_node), history_len=info_mgr.cell_length())
#                                cell_wl_history[position_name(net_node)] = [0 for _ in range(len(cell_wl_history[random.choice(cell_wl_history.keys())]))]
                            inserted = True
                            msg_mgr.add_msg("[INFO] Added new node : real_pos {0} - automata_pos {1}".format(
                                                                                    str(net_node.position),
                                                                                    str(cell.position)))
                        else:
                            position = random2dpos()
                else:
                    msg_mgr.add_msg("[INFO] > Automata full")
#                print len(automata.elements), automata.full()
            elif e.type == KEYDOWN and e.key == K_c:
                cell = random.choice(automata.elements.keys())
                for _ in range(random.randint(10,60)):
                    j = real_net.job(info_mgr.get_next_jobid(), start_time, random.randint(5, 2000))
                    automata.elements[cell].element.add_job(j)
#                    jobid += 1
#                    new_jobs += 1
            elif e.type == KEYDOWN and e.key == pygame.locals.K_ESCAPE:
                cmd_str = "a,0-0,100,350,1"
                cmd_type, params = analyze_cmd(cmd_str)
                if cmd_type:
                    if cmd_type == ADD_JOB and len(params) == 4:
                        cell_pos = params[0]
                        num_jobs = int(params[1])
                        work_requested = int(params[2])
                        min_workload=int(params[3])
                        if cell_pos in automata.elements:
                            for _ in range(num_jobs):
                                j = real_net.job(info_mgr.get_next_jobid(), start_time, work_requested, min_workload)
                                automata.elements[cell_pos].element.add_job(j)
#                                jobid +=1 
#                                new_jobs +=1
                            msg_mgr.add_msg("[INFO] Added {0} new jobs to {1}".format(str(num_jobs), cell_pos))
                cmd_str = ""
            elif e.type == USEREVENT or (e.type == KEYDOWN and e.key == pygame.locals.K_RETURN):
                cmd_type, params = analyze_cmd(cmd_str)
                if cmd_type:
                    if cmd_type == ADD_JOB and len(params) == 4:
                        try:
                            cell_pos = params[0]
                            num_jobs = int(params[1])
                            work_requested = int(params[2])
                            min_workload=int(params[3])
                            if cell_pos in automata.elements:
                                for _ in range(num_jobs):
                                    j = real_net.job(info_mgr.get_next_jobid(), start_time, work_requested, min_workload)
                                    automata.elements[cell_pos].element.add_job(j)
#                                    jobid +=1 
#                                    new_jobs +=1
                                msg_mgr.add_msg("[INFO] Added {0} new jobs to {1}".format(str(num_jobs), cell_pos))
                        except Exception as e:
                            msg_mgr.add_msg("[INFO] Bad command : {0}".format(e))
                    elif cmd_type == ADD_NODE and len(params) == 2:
                        if not automata.full():
                            position = (int(params[0]), int(params[1]))
                            inserted = False
                            while not inserted and not automata.full():
                                if not (position in automata.elements_position()):
                                    net_node = real_net.node(position)
                                    cell = ca.ca_cell(element = net_node)
                                    if automata.add_element(cell):
                                        info_mgr.add_cell(position_name(net_node), history_len=info_mgr.cell_length(), 
                                                          default_value=0)
#                                        cell_wl_history[position_name(net_node)] = [0 for _ in range(len(cell_wl_history[random.choice(cell_wl_history.keys())]))]
                                    inserted = True
                                    msg_mgr.add_msg("[INFO] Added new node : real_pos {0} - automata_pos {1}".format(
                                                                                            str(net_node.position),
                                                                                            str(cell.position)))
                                else:
                                    msg_mgr.add_msg("[ERROR] Can't add node in {0}".format(str(position)))
                cmd_str = ""
            elif e.type == KEYDOWN and e.key == pygame.locals.K_F3:
                visualize_graphs = not visualize_graphs
            elif e.type == KEYDOWN and e.key == pygame.locals.K_F5:
                end = True
            elif e.type == KEYDOWN:
                cmd_str += str(e.unicode)

        automata.update(current_time - start_time)

#        moved_jobs += new_moved_jobs
#        ended_jobs += new_ended_jobs
#        move_of_ended_jobs += new_move_of_ended_jobs

#        moved_jobs += automata.update(current_time - start_time)

        screen.fill((250, 250, 250))

        grph_act_chr = ""
        if not visualize_graphs:
            grph_act_chr = "not "

        image = font.render("Iter : {0:5} | Time : {1:10} | Framerate {2:5} | Plotting {3}active".format(i, current_time/1000.0, 
                                                                                                          1000/(1+(current_time - start_time)),
                                                                                                          grph_act_chr),
                            True, (0,0,0))
        
        r = image.get_rect()
        r.top = 5
        r.left = 5
        
        screen.blit(image, r)
        
        for switch in info_mgr.switches.values():
            cell = switch[0]
            color = switch[1]
            alpha = float(cell.element.already_moved) / float(ca.MOVE_COOLDOWN)
            image = pygame.Surface((SQUARE_DIM+10, SQUARE_DIM+10))
            image.set_alpha(alpha * 255)
            image.fill(color)
            rect = image.get_rect()
            rect.top = (cell.position[1] * (SQUARE_DIM + CELL_PADDING) + AUTOMATA_OFFSET_Y) * GRID_FRAC - 5
            rect.left =(cell.position[0] * (SQUARE_DIM + CELL_PADDING) + AUTOMATA_OFFSET_X) * GRID_FRAC - 5
            
            screen.blit(image, rect)

        for cell in automata.elements:
            image = pygame.Surface((SQUARE_DIM, SQUARE_DIM))
            wl = min(automata.elements[cell].element.workload / automata.elements[cell].element.max_workload, 1.0)
            color = (int(wl*255), 0, int((1.0 -wl)*255))

            if i%C_INTERVAL == 0:
                node_name = position_name(automata.elements[cell].element)
                info_mgr.add_cell_wl(node_name, wl*100)
#                cell_wl_history[node_name].append(wl*100)
#                if len(cell_wl_history[node_name]) > MAX_WL_HISTORY:
#                    cell_wl_history[node_name].pop(0)
            
            image.fill(color)
            
            rect = image.get_rect()
            rect.top = (automata.elements[cell].position[1] * (SQUARE_DIM + CELL_PADDING) + AUTOMATA_OFFSET_Y) * GRID_FRAC
            rect.left =(automata.elements[cell].position[0] * (SQUARE_DIM + CELL_PADDING) + AUTOMATA_OFFSET_X) * GRID_FRAC
            
            screen.blit(image, rect)
            
            rect = image.get_rect()
            rect.top = (automata.elements[cell].element.position[1] * (SQUARE_DIM + CELL_PADDING) + GEO_OFFSET_Y) * GRID_FRAC
            rect.left =(automata.elements[cell].element.position[0] * (SQUARE_DIM + CELL_PADDING) + GEO_OFFSET_X) * GRID_FRAC
            
            screen.blit(image, rect)
            
            wl_font = font.render("WL:{0}".format(str(automata.elements[cell].element.workload / 
                                                               automata.elements[cell].element.max_workload)),
                                  True, (255,255,255))
            rect = wl_font.get_rect()
            rect.top =  (automata.elements[cell].position[1] * (SQUARE_DIM + CELL_PADDING)) * GRID_FRAC + AUTOMATA_OFFSET_Y +1
            rect.left = (automata.elements[cell].position[0] * (SQUARE_DIM + CELL_PADDING)) * GRID_FRAC + AUTOMATA_OFFSET_X +1
            
            screen.blit(wl_font, rect)
            
            rect = image.get_rect()
            rect.top = (automata.elements[cell].element.position[1] * (SQUARE_DIM + CELL_PADDING) + GEO_OFFSET_Y) * GRID_FRAC +1
            rect.left =(automata.elements[cell].element.position[0] * (SQUARE_DIM + CELL_PADDING) + GEO_OFFSET_X) * GRID_FRAC +1
            
            screen.blit(wl_font, rect)
            
            wl_font = small_font.render("ID:{0},{1}".format(automata.elements[cell].element.position[0], 
                                                            automata.elements[cell].element.position[1]),
                                  True, (255,255,255))
            rect = wl_font.get_rect()
            rect.top =  (automata.elements[cell].position[1] * (SQUARE_DIM + CELL_PADDING) + AUTOMATA_OFFSET_Y) * GRID_FRAC +15
            rect.left = (automata.elements[cell].position[0] * (SQUARE_DIM + CELL_PADDING) + AUTOMATA_OFFSET_X) * GRID_FRAC +1
            
            screen.blit(wl_font, rect)
            
            rect = image.get_rect()
            rect.top = (automata.elements[cell].element.position[1] * (SQUARE_DIM + CELL_PADDING)  + GEO_OFFSET_Y) * GRID_FRAC +15
            rect.left =(automata.elements[cell].element.position[0] * (SQUARE_DIM + CELL_PADDING)  + GEO_OFFSET_X) * GRID_FRAC +1
            
            screen.blit(wl_font, rect)
        
        wl_font = font.render("CELLULAR AUTOMATA",
                              True, (0,0,0))
        rect = wl_font.get_rect()
        rect.top =  ((math.sqrt(ca.MAX_CELLS)/2) * (SQUARE_DIM + CELL_PADDING)) * GRID_FRAC + AUTOMATA_OFFSET_Y +40
        rect.left = SQUARE_DIM
    
        screen.blit(wl_font, rect)
        
        wl_font = font.render("REAL NET",
                              True, (0,0,0))
        rect = wl_font.get_rect()
        rect.top =  ((math.sqrt(ca.MAX_CELLS)/2) * (SQUARE_DIM + CELL_PADDING)) * GRID_FRAC + AUTOMATA_OFFSET_Y +40
        rect.left = ((math.sqrt(ca.MAX_CELLS)) * (SQUARE_DIM + CELL_PADDING)) + AUTOMATA_OFFSET_X/2 + SQUARE_DIM
    
        screen.blit(wl_font, rect)

        wl_font = font.render(cmd_str,
                              True, (0,0,0))
        rect = wl_font.get_rect()
        rect.top =  20
        rect.left = 10
    
        screen.blit(wl_font, rect)
         
        msg_y_offset = 0    
        for msg in msg_mgr.msgs:
            wl_font = font.render(msg,
                                  True, (0,0,0))
            rect = wl_font.get_rect()
            rect.top = LOG_OFFSET_Y + msg_y_offset * (MSG_DIM + 5)
            rect.left= LOG_OFFSET_X
            msg_y_offset +=1
            
            screen.blit(wl_font, rect)
            
                
#        wls = [automata.elements[cell].element.current_workload for cell in automata.elements]
#        tot_wl = numpy.average(wls)
#        
#        tot_wl_var = numpy.var(wls)

        if i%C_INTERVAL == 0:
            info_mgr.add_cell_distance(automata.calc_geo_distance())
            info_mgr.calc_frame_values()

                
#        if i%C_INTERVAL == 0:
            
            
#            wl_history.append(tot_wl)
#            wl_variance_history.append(tot_wl_var)
#            new_jobs_history.append(new_jobs)
#            new_jobs = 0
#            moved_jobs_history.append(moved_jobs)
#            moved_jobs = 0
#            medium_distance_history.append(automata.calc_geo_distance())
#            if len(wl_history) > MAX_WL_HISTORY:
#                wl_history.pop(0)
#                wl_variance_history.pop(0)
#                new_jobs_history.pop(0)
#                moved_jobs_history.pop(0)                         
#                medium_distance_history.pop(0)
                
        if i%C_INTERVAL and visualize_graphs:         
#            wl_fig.clf()
                                    
            plt.clf()
            ax1 = plt.subplot(6,1,1)
            ax1.set_title("Load average")
            ax1.plot(info_mgr.wl_history)
            for cell in automata.elements:
                node_name = position_name(automata.elements[cell].element)
                ax1.plot(info_mgr.cell_workload_history[node_name], c=(0,1,0,0.35))
            ax1.plot(activate_line, c=(1.0,0,0))
            ax1.plot(deactivate_line, c=(0.7, 0, 0))
            pylab.ylim([-0.5, 100])
            
            ax2 = plt.subplot(6,1,2, sharex=ax1)
            ax2.set_title("Load variance")
            ax2.plot(info_mgr.wl_variance_history)
            pylab.ylim([-0.5, 1000])
            
            ax3 = plt.subplot(6,1,3, sharex=ax1)
            ax3.set_title("New Jobs")
            ax3.plot(info_mgr.new_jobs_history)
            pylab.ylim([-0.1,500])
                        
            ax4 = plt.subplot(6,1,4, sharex=ax1)
            ax4.set_title("Moved Jobs")
            ax4.plot(info_mgr.moved_jobs_history)
            pylab.ylim([-0.1, 150])
            
            ax5 = plt.subplot(6,1,5, sharex=ax1)
            ax5.set_title("Average neighbor distance")
            ax5.plot(info_mgr.medium_distance_history)
            pylab.ylim([-0.1, math.sqrt(ca.MAX_CELLS)*2])
            
            ax6 = plt.subplot(6,1,6, sharex=ax1)
            ax6.set_title("Average move before end")
            ax6.plot(info_mgr.average_moved_times)
            pylab.ylim([-0.1, 5])
                        
            pylab.xlim([0, MAX_WL_HISTORY])
            
            
#            
            plt.tight_layout(0.4, 0.5, 1.0)
#            
##            wl_graph_canvas.draw()
##    
##            wl_renderer = wl_graph_canvas.get_renderer()
##            wl_raw_data = wl_renderer.tostring_rgb()
##                
##            wl_size = wl_graph_canvas.get_width_height()
##            wl_surf = pygame.image.fromstring(wl_raw_data, wl_size, "RGB")
            plt.draw()
##        screen.blit(wl_surf, (650, 5))            
                        
        pygame.display.update()
        
        start_time = current_time
    info_mgr.finalize_stats()
    return 0
    
if __name__ == "__main__":
    main()