#!/bin/bash -l

count=`squeue -u bing|grep bing|wc -l`
cut=10
lsb_dir=/gpfs/alpine/stf008/scratch/bing/dl/lsb_acct


rm curr_*
touch complete
touch running

process(){
    local per=$1
    local pdir=$lsb_dir/$per
    local sub=${per}.sh
    local job=${per}.py

    if [[ `cat complete` != *"$per"* && `cat running` != *"$per"* && $count -lt $cut ]]; then
        cp rhea_job.sh $sub
        sed -i -e "s/JOB/$per/g" $sub
        cp template.py $job
        sed -i -e "s/JOB/$per/g" $job
        submitted=`sbatch $sub`
        echo "running $submitted"
        echo $per>>running
        count=$(($count+1)) 
   
    elif [[ $count -ge $cut ]]; then
        echo "rhea job limitation: $count jobs submitted"
    elif [[ `cat complete` == *"$per"* ]]; then
        echo "$per completed"
    elif [[ `cat running` == *"$per"* ]]; then
        echo "$per is running"

    fi
}
for per in `ls $lsb_dir`; do
    process $per
done
