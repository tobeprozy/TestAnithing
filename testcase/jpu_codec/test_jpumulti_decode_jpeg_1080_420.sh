#!/bin/bash
rm -rf *.log *.txt

image=1920x1080_yuvj420.jpg
tpu_id=0
thread_num=10
loop=1000

jpumulti 1 $image ${loop} ${thread_num} 0 ${tpu_id} >>${image}_tpu_${tpu_id}.log &

echo "Start Wait End..."
while true; do
    jpumulti_num=$(ps aux | grep jpumulti | grep -v "grep" | wc -l)
    echo "running jpumulti num: ${jpumulti_num}"
    if [[ "$jpumulti_num" == "0" ]]; then
        break
    fi
    sleep 3
done
echo "Start Calc fps..."

for ((j = 0; j < $thread_num; j++)); do
    {
        cat ${image}_tpu_${tpu_id}.log | grep Decoder${j} | awk -F ':' '{print $2}' | tr -d ' ' >>time_all.txt
        cat time_all.txt | awk '{sum+=$1} END {print sum}' >timesum.txt
    }
done

total_time=$(echo "scale=2; $(<timesum.txt)/${thread_num}" | bc)
echo "total_time: ${total_time}"

total_frame=$(echo "$((${loop} * ${thread_num}))")
echo "total_frame: ${total_frame}"

speed=$(echo "scale=2; ${total_frame}/${total_time}" | bc)
echo "speed: ${speed}fps"

rm *.log *.txt
