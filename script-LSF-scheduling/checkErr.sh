jobs=`ls logs/e.*`

pro(){
    local log=$1
    cat $log
    echo "$log done"
}
for log in $jobs; do
    pro $log
done
