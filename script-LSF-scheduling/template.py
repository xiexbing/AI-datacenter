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
data_dir = "dir_for_original_log"
result_dir = "result"

def read_file(data_file):

    d_f = open(data_file, 'r')
    dfile = d_f.readlines()
    d_f.close()

    return dfile

def process_line(line, rdir, edir):

    inform = line.split('"')
    status = inform[1]
    times_nodes = inform[4].split()
    if len(times_nodes) != 9:
        efile = open(edir, 'a')
        wline = 'err:status ' + line
        efile.write(wline)
        efile.truncate()
        efile.close()
        return
        
    else:
        finishTime = times_nodes[0]
        jobID = times_nodes[1]
        userID = times_nodes[2]
        numCores = times_nodes[4]
        numNodes = int((int(numCores) -1)/42)
        submitTime = times_nodes[5]
        beginTime = times_nodes[8]
        if beginTime == '0':
            efile = open(edir, 'a')
            wline = 'err:beginTime ' + line
            efile.write(wline)
            efile.truncate()
            efile.close()
            return
        else: 
            userName = inform[5]
            nodes = []
            if 'batch' in inform[27] and 'batch' != inform[27]:
                batchNode = inform[27]
                nstart = 29
                nend = nstart + int(numCores)*2 -3
            elif 'batch' in inform[31] and 'batch' != inform[31]:
                batchNode = inform[31]
                nstart = 33
                nend = nstart + int(numCores)*2 -3
            else:
                efile = open(edir, 'a')
                wline = 'err:nodeStart ' + line
                efile.write(wline)
                efile.truncate()
                efile.close()
                return
            for item in inform[nstart:nend]:
                if item not in nodes and item != ' ':
                    nodes.append(item)
            if len(nodes) != numNodes:
                print ('err:numNodes: ', len(nodes), numNodes, inform[nstart-2:nend])
                efile = open(edir, 'a')
                wline = 'err:numNodes ' + line
                efile.write(wline)
                efile.truncate()
                efile.close()
                return
            else:
                exitStatus = inform[nend].split()[0]
                newStart = nend + 1
                err = 1 
                for i, item in enumerate(inform[newStart:]):
                    if numCores in item and batchNode == inform[newStart+i+1]:
                        nameIndex = newStart+i-15
                        projName = inform[nameIndex]
                        if projName != '0': 
                            print (inform[nameIndex:])
                            record_line = [status, projName, userName, jobID, userID, submitTime, beginTime, finishTime, exitStatus, len(nodes)] + nodes
                            wline = ' '.join(str(f) for f in record_line) + '\n'
                            rfile = open(rdir, 'a')
                            rfile.write (wline)
                            rfile.truncate()
                            rfile.close()
                            err = 0
                            return
                        else:
                            print ('err:projName: ', inform[nameIndex:])
                            efile = open(edir, 'a')
                            wline = 'err:projName ' + line
                            efile.write(wline)
                            efile.truncate()
                            efile.close()
                            return
 
                if err == 0:
                    efile = open(edir, 'a')
                    wline = 'err:unCatch ' + line
                    efile.write(wline)
                    efile.truncate()
                    efile.close()
                    return
          

def process_log(job):

    job_dir = os.path.join(data_dir, job)
    rdir = os.path.join(result_dir, job) 
    efile = job + ".err"
    edir = os.path.join(result_dir, efile) 


    data = read_file(job_dir)

    for line in data:
        process_line(line, rdir, edir)
     

def main(): 

    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)    

    rdir = os.path.join(result_dir, job_name)
    rfile = open(rdir, 'a')
    start_line = "#1.jobStatus, 2.projName, 3.userName, 4.jobID, 5.userID, 6.submitTime, 7.beginTime, 8.finishTime, 9.exit_status, 10.len(nodes), 11.nodeList" + '\n'
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
