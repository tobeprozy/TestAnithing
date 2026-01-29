#!/bin/bash

video=jellyfish-3-mbps-hd-h264.mkv
tpu_ids=(0)
thread_num=25 
# sleep_time=100
decode_type=h264_bm

rm -rf *.log
rm -rf fpssum.txt  fps.txt  framesum.txt  frame.txt  speed.txt  timeavg.txt  timesum.txt  time.txt

for tpu_id in ${tpu_ids[@]}
do
{
    for ((thread=0; thread<$thread_num; thread++))
    do
    {
        # decode 1000 frame
        nohup ffmpeg -benchmark -stream_loop -1 -extra_frame_buffer_num 5 -output_format 0 -zero_copy 1 -sophon_idx ${tpu_id} -c:v ${decode_type} -i $video -vframes 1000 -f null /dev/null >> ${video}_thread_${thread}_tpu_${tpu_id}.log 2>&1 &
    } &
    done
}
done

echo "Start Wait End..."

# sleep ${sleep_time}

# check if ffmpeg finished
while ps aux | grep -q '[f]fmpeg'; do
    echo "Wait until no ffmpeg process ..."
    sleep 1
done

echo "===== All ffmpeg process exit ====="

echo "Start Calc fps..."

for tpu_id in ${tpu_ids[@]}
do
{
    for ((thread=0; thread<$thread_num; thread++))
    do
        frame_index=0
        for((a=1; a<20; a++))
        do
            str=$(cat ${video}_thread_${thread}_tpu_${tpu_id}.log | tail -n ${a}|head -n 1)
            # echo $str
            keyword=$(echo $str |grep "frame=")
            # echo $keyword
            if [[ $keyword != "" ]];
            then
            frame_index=${a}
            break
            fi
        done
        time_index=0
        for((a=1; a<20; a++))
        do
                str=$(cat ${video}_thread_${thread}_tpu_${tpu_id}.log | tail -n ${a}|head -n 1)
                # echo $str
                keyword=$(echo $str |grep "rtime=")
                # echo $keyword
                if [[ $keyword != "" ]];
                then
                    time_index=${a}
                    break
                fi
        done

        cat ${video}_thread_${thread}_tpu_${tpu_id}.log | tail -n $frame_index|head -n 1| awk -F '=' '{print $3}'|tr -d 'a-z'|tr -d ' ' >> fps.txt    #fps
        cat ${video}_thread_${thread}_tpu_${tpu_id}.log | tail -n $frame_index|head -n 1| awk -F '=' '{print $2}'|tr -d 'a-z'|tr -d ' ' >> frame.txt    #frames
        cat ${video}_thread_${thread}_tpu_${tpu_id}.log | tail -n $time_index|head -n 1| awk -F '=' '{print $4}'|tr -d 'a-z'|tr -d ' ' >> time.txt    #frames
        cat fps.txt | awk '{sum+=$1} END {print sum}' > fpssum.txt
        cat frame.txt | awk '{sum+=$1} END {print sum}' > framesum.txt
        cat time.txt | awk '{sum+=$1} END {print sum}' > timesum.txt
    done
}
done

echo "tpu_id: $tpu_id"
echo "total_frames: $(<framesum.txt)"
task_num=$(cat frame.txt | grep "." -c)
cat timesum.txt | awk '{print $1/'$task_num'}' > timeavg.txt
echo "avg_time: $(<timeavg.txt)"
f_sum=$(<framesum.txt)
time_avg=$(<timeavg.txt)
awk 'BEGIN{printf "%.2f\n",'$f_sum'/'$time_avg'}' > speed.txt
speed=$(<speed.txt)
echo "speed: ${speed}"