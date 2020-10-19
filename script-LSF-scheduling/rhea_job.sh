#!/bin/bash -l
#SBATCH -A projName 
#SBATCH -t 24:00:00
#SBATCH -N 1 
##SBATCH -d PREV
#SBATCH -J JOB 
#SBATCH -o o.JOB
#SBATCH -e e.JOB

module load python/3.7.0-anaconda3-2018.12

srun -n 1 python JOB.py
