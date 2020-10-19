import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    mpl.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import shutil
import subprocess as sp

job_name = "JOB"
complete = "/ccs/home/bing/dl-ornl/script"
data_dir = "/gpfs/alpine/stf008/scratch/bing/dl/lsb_acct"
result_dir = "result"

def read_file(data_file):

    d_f = open(data_file, 'r')
    dfile = d_f.readlines()
    d_f.close()

    return dfile

def process_line(line, rdir):

    err = 0
 
    inform = line.split('"')
    nodes = inform[26].split()

    if len(nodes) == 4:
        fdir = os.path.join(result_dir, 'error_records')
        fd = open(fdir, 'a')
        wline = 'err: format nodes: ' + line
        fd.write(wline)
        fd.truncate()
        fd.close()
        
        err = 1
    else:
        status = inform[1]
        userName = inform[5]

        ids = inform[4].split()
        if len(ids) == 9:
            finishTime = ids[0]
            jobID = ids[1]
            userID = ids[2]
            num_cores = int(ids[4]) - 1
            submitTime = ids[5]
            beginTime = ids[6]
            termTime = ids[7]
            startTime = ids[8]
           
            nodes = []
            for i in inform[29:29+num_cores*2-1]:
                if i != ' ' and i not in nodes:
                    nodes.append(i)
            if num_cores/42 != len(nodes):
                print (num_cores, len(nodes), nodes)
                wline = 'err: number of nodes ' + num_cores + ' ' + len(nodes)  + line
                fdir = os.path.join(result_dir, 'error_records')
                fd = open(fdir, 'a')
                fd.write(wline)
                fd.truncate()
                fd.close()

                err = 1

            else:
                new_start = 29+num_cores*2-1
                command = inform[new_start+3].split()
                time = 'time'
                for i, per in enumerate(command):
                    if '-W' == per and "BSUB" in command[i-1]:
                        time = command[i+1].replace("BSUB", "").replace(";", "").replace("#", "").replace("-", "")
                    if '-P' == per and "BSUB" in command[i-1]:
                        proj = command[i+1].replace("BSUB", "").replace(";", "").replace("#", "").replace("-", "")
                try:
                    proj
                except NameError:
                    wline = 'err: proj name ' + line
                    fdir = os.path.join(result_dir, 'error_records')
                    fd = open(fdir, 'a')
                    fd.write(wline)
                    fd.truncate()
                    fd.close()

                    err = 1

                if err == 0:
                    after_command = new_start + 4
                    for i, per in enumerate(inform[after_command:]):
                        if per == proj:
                            useful = i+after_command
                            memory = inform[useful+5].split()[1:]
                            max_res_memory = memory[0]
                            virtual_memory = memory[1]
                            exit_status = inform[new_start].split()[0]
                            record_line = [status, proj, userName, jobID, userID, submitTime, startTime, finishTime, max_res_memory, virtual_memory, exit_status, time, len(nodes)] + nodes
                            wline = ' '.join(str(f) for f in record_line) + '\n'
                            rfile = open(rdir, 'a')
                            rfile.write (wline)
                            rfile.truncate()
                            rfile.close()
                            break


        else:
            wline = 'err: miss inform ids '  + line
            fdir = os.path.join(result_dir, 'error_records')
            fd = open(fdir, 'a')
            fd.write(wline)
            fd.truncate()
            fd.close()
            err = 1
 
def process_log(job):

    job_dir = os.path.join(data_dir, job)
    rdir = os.path.join(result_dir, job) 
    data = read_file(job_dir)

    for line in data:
        process_line(line, rdir)
     

def main(): 

    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)    

    rdir = os.path.join(result_dir, job_name)
    rfile = open(rdir, 'a')
    start_line = "#1.job status, 2.proj Name, 3.userName, 4.jobID, 5.userID, 6.submitTime, 7.startTime, 8.finishTime, 9.max_res_memory, 10.virtual_memory, 11.exit_status, 12.time, 13.len(nodes), 14.nodeList" + '\n'
    rfile.write(start_line)
    rfile.truncate()
    rfile.close()

    process_log(job_name)
    cfile = open("complete", 'a')
    line = job_name + '\n'
    cfile.write(line)
    cfile.truncate()
    cfile.close() 
main()                                   
