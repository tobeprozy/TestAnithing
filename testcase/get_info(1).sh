#!/bin/bash

shopt -s compat31
temp_file=$(mktemp)
trap 'rm -f "$temp_file"' EXIT

function panic()
{
    if [ $# -gt 0 ]; then
        echo "" >&1
        echo "ERROR: $@" >&1
        echo "" >&1
    fi
    exit 1
}

function file_validate()
{
    local file
    file=$(eval echo \$1)
    [ -r ${file} ] || panic "$i \"$file\" is not readable"
}

function suser() {
    sudo -k || panic "failed to kill superuser privilege"
    sudo -v || panic "failed to get superuser privilege"
}

# [jump byte] [size] [file]
function od_read_char() {
    od -An -v -j ${1} -N ${2} -t c -w${2} ${3} 2>/dev/null | sed 's| \\0| |g' | sed 's| \\n| |g' | sed 's| \\r| |g' | tr -d ' '
}

# [ion path]
function get_ion_usage()
{
    local path
    path=$(eval echo \$1)
    if [ -f "$path"/total_mem ]; then
        total=$(cat "$path"/total_mem 2>/dev/null)
        alloc=$(cat "$path"/alloc_mem 2>/dev/null)
        usage=$(echo "scale=2; ($alloc / $total) * 100" | bc)
        echo "$usage"
    else
        echo "0"
    fi
}

function jsonq() {
    json=$(cat)
    awk -v json="$json" -v json_orgi="$json" -v key="$1" '
    function strlastchar(s) {
        return substr(s, length(s), 1)
    }
    function startwith(s, c) {
        start = substr(s, 1, 1)
        return start == c
    }
    function endwith(s, c) {
        return strlastchar(s) == c
    }
    function innerstr(s) { # 取出括号/引号内的内容
        return substr(s, 2, length(s)-2)
    }
    function strindex(s, n) { # 字符串通过下标取值，索引是从1开始的
        return substr(s, n, 1)
    }
    function trim(s) {
        sub("^[ \n]*", "", s);
        sub("[ \n]*$", "", s);
        return s
    }
    function findValueByKey(s, k) {
        if ("\""k"\"" != substr(s, 1, length(k)+2)) {exit 0}
        s = trim(s)
        start = 0; stop = 0; layer = 0
        for (i = 2 + length(k) + 1; i <= length(s); ++i) {
            lastChar = substr(s, i - 1, 1)
            currChar = substr(s, i, 1)
            if (start <= 0) {
                if (lastChar == ":") {
                    start = currChar == " " ? i + 1: i
                    if (currChar == "{" || currChar == "[") {
                        layer = 1
                    }
                }
            } else {
                if (currChar == "{" || currChar == "[") {
                    ++layer
                }
                if (currChar == "}" || currChar == "]") {
                    --layer
                }
                if ((currChar == "," || currChar == "}" || currChar == "]") && layer <= 0) {
                    stop = currChar == "," ? i : i + 1 + layer
                    break
                }
            }
        }
        if (start <= 0 || stop <= 0 || start > length(s) || stop > length(s) || start >= stop) {
            exit 0
        } else {
            return trim(substr(s, start, stop - start))
        }
    }
    function unquote(s) {
        if (startwith(s, "\"")) {
            s = substr(s, 2, length(s)-1)
        }
        if (endwith(s, "\"")) {
            s = substr(s, 1, length(s)-1)
        }
        return s
    }
    BEGIN{
        if (match(key, /^\./) == 0) {exit 0;}
        sub(/\][ ]*\[/,"].[", key)
        split(key, ks, ".")
        if (length(ks) == 1) {print json; exit 0}
        for (j = 2; j <= length(ks); j++) {
            k = ks[j]
            if (startwith(k, "[") && endwith(k, "]") == 1) { # [n]
                idx = innerstr(k)
                currentIdx = -1
                # 找匹配对
                pairs = ""
                json = trim(json)
                if (startwith(json, "[") == 0) {
                    exit 0
                }
                start = 2
                cursor = 2
                for (; cursor <= length(json); cursor++) {
                    current = strindex(json, cursor)
                    if (current == " " || current == "\n") {continue} # 忽略空白
                    if (current == "[" || current == "{") {
                        if (length(pairs) == 0) {start = cursor}
                        pairs = pairs""current
                    }
                    if (current == "]" || current == "}") {
                        if ((strlastchar(pairs) == "[" && current == "]") || (strlastchar(pairs) == "{" && current == "}")) {
                            pairs = substr(pairs, 1, length(pairs)-1) # 删掉最后一个字符
                            if (pairs == "") { # 匹配到了所有的左括号
                                currentIdx++
                                if (currentIdx == idx) {
                                    json = substr(json, start, cursor-start+1)
                                    break
                                }
                            }
                        } else {
                            pairs = pairs""current
                        }
                    }
                }
            } else {
                # 到这里，就只能是{"key": "value"}或{"key":{}}或{"key":[{}]}
                pairs = ""
                json = trim(json)
                if (startwith(json, "[")) {exit 0}
                #if (!startwith(json, "\"") || !startwith(json, "{")) {json="\""json}
                # 找匹配的键
                start = 2
                cursor = 2
                noMatch = 0
                for (; cursor <= length(json); cursor++) {
                    current = strindex(json, cursor)
                    if (current == " " || current == "\n" || current == ",") {continue} # 忽略空白和逗号
                    if (substr(json, cursor, length(k)+2) == "\""k"\"") {
                        json = findValueByKey(substr(json, cursor, length(json)-cursor+1), k)
                        break
                    } else {
                        noMatch = 1
                    }
                    if (noMatch) {
                        pos = match(substr(json, cursor+1, length(json)-cursor), /[^(\\")]"/)
                        ck = substr(substr(json, cursor+1, length(json)-cursor), 1, pos)
                        t = findValueByKey(substr(json, cursor, length(json)-cursor+1), ck)
                        tLen = length(t)
                        sub(/\\/, "\\\\", t)
                        pos = match(substr(json, cursor+1, length(json)-cursor), t)
                        if (pos != 0) {
                            cursor = cursor + pos + tLen
                        }
                        noMatch = 0
                        continue
                    }
                }
            }
        }
        if (json_orgi == json) { print;exit 0 }
        print unquote(json)
    }'
}

# suser
file_validate /proc/cpuinfo
file_validate /proc/stat

if [[ "$1" == "server" ]] && [[ ! "$2" == "" ]] && [[ ! "$3" == "" ]]; then
	log_file="$(readlink -f "$2")"
	loop_wait_time="$3"
	get_info_pwd="$(readlink -f "$0")"
	echo "log write to file:${log_file}"
	echo "wait time in loop(s):${loop_wait_time}"
	echo "get_info pwd:${get_info_pwd}"
	read -p "Do you acknowledge the information above? (y/n) " -n 1 -r
	echo ""
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		systemctl stop sophon-get-info-server.service
		systemctl reset-failed sophon-get-info-server.service
		systemd-run --unit=sophon-get-info-server /usr/bin/bash -c "source /etc/profile; ldconfig; while true; do sleep ${loop_wait_time}; bash ${get_info_pwd} 2>/dev/null 1>> ${log_file}; done;"
		sleep 3
		systemctl status sophon-get-info-server.service --no-page -l
		exit 0
	else
		exit -1
	fi
fi

# BOOT_TIME(S)
BOOT_TIME=0
BOOT_TIME=$(cat /proc/uptime 2>/dev/null | awk '{print $1}')

# DATE_TIME
DATE_TIME=$(date +"%Y-%m-%d %H:%M:%S %Z")

# CPU NAME
CPU_MODEL=$(awk -F': ' '/model name/{print $2; exit}' /proc/cpuinfo)
# ! [[ "$CPU_MODEL" == "" ]] || panic "cannot get cpu model from /proc/cpuinfo"

# WORK MODE
SOC_MODE_CPU_MODEL=("bm1684x" "bm1684" "bm1688" "cv186ah")
WORK_MODE="PCIE"
for element in "${SOC_MODE_CPU_MODEL[@]}"; do
    if [ "$element" == "$CPU_MODEL" ]; then
        WORK_MODE="SOC"
        break
    fi
done
if [[ "${WORK_MODE}" == "PCIE" ]]; then
    file_validate /dev/bmdev-ctl
fi

# DDR INFO
DDR_SIZE=0
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        DTS_MEM_FILE="/proc/device-tree/memory/reg"
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        DTS_MEM_FILE="/proc/device-tree/memory*/reg"
    fi
    DDR_SIZE=0
    od --endian=big -An -v -t u4 -w16 ${DTS_MEM_FILE} | while read -r line
    do
        size1=$(echo "$line" | awk '{print $3}')
        size2=$(echo "$line" | awk '{print $4}')
        ddr_s=$(( size1 * 1024 * 1024 * 1024 * 4 + size2 ))
        DDR_SIZE=$((DDR_SIZE + ddr_s))
        echo "${DDR_SIZE}" > "$temp_file"
    done
    DDR_SIZE=$(cat "$temp_file" | tr -d '\0')
    DDR_SIZE=$(( DDR_SIZE / 1024 / 1024 ))
fi

# EMMC_SIZE
EMMC_SIZE=0
if [[ "${WORK_MODE}" == "SOC" ]]; then
    EMMC_SIZE_BYTE=$(lsblk -b 2>/dev/null | grep "^mmcblk0 " | awk '{print $4}')
    EMMC_SIZE=$(( EMMC_SIZE_BYTE / 1024 / 1024 ))
fi

# MEM_INFO
SYSTEM_MEM="0"
TPU_MEM="0"
VPU_MEM="0"
VPP_MEM="0"
if [[ "${WORK_MODE}" == "SOC" ]]; then
    SYSTEM_MEM=$(vmstat -s 2>/dev/null | grep "total memory" | awk '{print $1}')
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        TPU_MEM=$(cat /sys/kernel/debug/ion/bm_npu_heap_dump/total_mem 2>/dev/null | tr -d '\0')
        VPU_MEM=$(cat /sys/kernel/debug/ion/bm_vpu_heap_dump/total_mem 2>/dev/null | tr -d '\0')
        VPP_MEM=$(cat /sys/kernel/debug/ion/bm_vpp_heap_dump/total_mem 2>/dev/null | tr -d '\0')
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        TPU_MEM=$(cat /sys/kernel/debug/ion/cvi_npu_heap_dump/total_mem 2>/dev/null | tr -d '\0')
        VPP_MEM=$(cat /sys/kernel/debug/ion/cvi_vpp_heap_dump/total_mem 2>/dev/null | tr -d '\0')
    fi
    SYSTEM_MEM=$(( SYSTEM_MEM / 1024 ))
    TPU_MEM=$(( TPU_MEM / 1024 / 1024 ))
    VPU_MEM=$(( VPU_MEM / 1024 / 1024 ))
    VPP_MEM=$(( VPP_MEM / 1024 / 1024 ))
fi

# SYSTEM_MEM_USAGE
SYSTEM_MEM_USAGE=$(free -k | grep '^Mem: ' | awk '{free=$7; total=$2; printf "%.2f\n", ((total-free)/total)*100}' 2>/dev/null)

# CPU_ALL_USAGE
unset CPU_ALL_USAGE
unset CPUS_USAGE
CPU_ALL_USAGE=""
CPUS_USAGE=""
function get_cpu_all() {
    cpu_num=$(cat /proc/stat 2>/dev/null | grep "^cpu" 2>/dev/null | wc -l)
    cpu_count=$((cpu_num - 1))
    sleep 0.5
    proc_stat1=$(cat /proc/stat)
    sleep 1
    proc_stat2=$(cat /proc/stat)
    awk -v proc_stat1="$(echo "$proc_stat1" | grep '^cpu ')" -v proc_stat2="$(echo "$proc_stat2" | grep '^cpu ')" '
    BEGIN {
        split(proc_stat1, a);
        split(proc_stat2, b);
        total1 = a[2] + a[3] + a[4] + a[5] + a[6] + a[7] + a[8];
        total2 = b[2] + b[3] + b[4] + b[5] + b[6] + b[7] + b[8];
        total = total2 - total1;
        user = (b[2] + b[3]) - (a[2] + a[3])
        kernel = b[4] - a[4];
        io_wait = b[6] - a[6];
        irq = (b[7] + b[8]) - (a[7] + a[8])
        idle = b[5] - a[5];
        usage = (total - idle) / total * 100;
        user_u = user / total * 100;
        ker_u = kernel / total * 100;
        irq_u = irq / total * 100;
        io_u = io_wait / total * 100;
        printf "%.2f,%.2f,%.2f,%.2f,%.2f ", usage, user_u, ker_u, io_u, irq_u;
    }' 2>/dev/null
    for ((i=0; i<cpu_count; i++)); do
        awk -v proc_stat1="$(echo "$proc_stat1" | grep "^cpu$i ")" -v proc_stat2="$(echo "$proc_stat2" | grep "^cpu$i ")" '
        BEGIN {
            split(proc_stat1, a);
            split(proc_stat2, b);
            total1 = a[2] + a[3] + a[4] + a[5] + a[6] + a[7] + a[8];
            total2 = b[2] + b[3] + b[4] + b[5] + b[6] + b[7] + b[8];
            total = total2 - total1;
            user = (b[2] + b[3]) - (a[2] + a[3])
            kernel = b[4] - a[4];
            io_wait = b[6] - a[6];
            irq = (b[7] + b[8]) - (a[7] + a[8])
            idle = b[5] - a[5];
            usage = (total - idle) / total * 100;
            user_u = user / total * 100;
            ker_u = kernel / total * 100;
            irq_u = irq / total * 100;
            io_u = io_wait / total * 100;
            printf "%.2f,%.2f,%.2f,%.2f,%.2f ", usage, user_u, ker_u, io_u, irq_u;
        }' 2>/dev/null
    done
    echo ""
}
{ read -r CPU_ALL_USAGE CPUS_USAGE; } <<< "$(get_cpu_all)"

# DTS_NAME
DTS_NAME=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        DTS_NAME=$(cat /proc/device-tree/info/file-name 2>/dev/null | tr -d '\0')
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        DTS_NAME=$(od_read_char 160 32 "/dev/mmcblk0boot1")
    fi
fi

# DEVICE_MODEL
DEVICE_MODEL=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        DEVICE_MODEL=$(grep "model" /sys/class/i2c-dev/i2c-1/device/1-0017/information 2>/dev/null | awk -F'"' '{print $4}')
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        DEVICE_MODEL_PRODUCT=$(od_read_char 208 16 "/dev/mmcblk0boot1")
        DEVICE_MODEL_MODULE_TYPE=$(od_read_char 112 16 "/dev/mmcblk0boot1")
        DEVICE_MODEL="${DEVICE_MODEL_PRODUCT} ${DEVICE_MODEL_MODULE_TYPE}"
    fi
fi

# CLKs
CPU_CLK=""
TPU_CLK=""
VPU_CLK=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        CPU_CLK=$(cat /sys/kernel/debug/clk/mpll_clock/clk_rate | tr -d '\0')
        TPU_CLK=$(cat /sys/kernel/debug/clk/tpll_clock/clk_rate | tr -d '\0')
        VPU_CLK=$(cat /sys/kernel/debug/clk/vpll_clock/clk_rate | tr -d '\0')
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        CPU_CLK=$(cat /sys/kernel/debug/clk/clk_a53pll/clk_rate | tr -d '\0')
        TPU_CLK=$(cat /sys/kernel/debug/clk/clk_tpll/clk_rate | tr -d '\0')
        VPU_CLK=$(cat /sys/kernel/debug/clk/clk_cam0pll/clk_rate | tr -d '\0')
        VPU_CLK=$(( VPU_CLK / 2 ))
    fi
fi

# SN
CHIP_SN=""
DEVICE_SN=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        # CHIP_SN=$(grep "product sn" /sys/class/i2c-dev/i2c-1/device/1-0017/information 2>/dev/null | awk -F'"' '{print $4}')
	CHIP_SN=$(od_read_char 0 32 "/sys/bus/nvmem/devices/1-006a0/nvmem")
	DEVICE_SN=$(od_read_char 512 32 "/sys/bus/nvmem/devices/1-006a0/nvmem")
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        CHIP_SN=$(od_read_char 0 32 "/dev/mmcblk0boot1")
        DEVICE_SN=$(od_read_char 32 32 "/dev/mmcblk0boot1")
    fi
fi

# MAC
ETH0_MAC=""
ETH1_MAC=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    ETH0_MAC=$(ip link show eth0 2>/dev/null | grep ether | awk '{print $2}')
    ETH1_MAC=$(ip link show eth1 2>/dev/null | grep ether | awk '{print $2}')
fi

# CHIP_TEMP
CHIP_TEMP=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    CHIP_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp | tr -d '\0')
    CHIP_TEMP=$(( CHIP_TEMP / 1000 ))
fi

# TPU_USAGE
TPU_USAGE=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        TPU_USAGE=$(cat /sys/class/bm-tpu/bm-tpu0/device/npu_usage | awk -F':' '{print $2}' | awk '{print $1}')
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        TPU_USAGE=$(cat /sys/class/bm-tpu/bm-tpu0/device/npu_usage | awk -F':' '{print $2}' | awk '{print $1}' | tr '\n' ' ' | sed 's/ *$//')
    fi
fi

# VPU_USAGE
VPU_USAGE=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        VPU_USAGE=$(cat /proc/vpuinfo | tr -d '\n' | grep -ao ':[0-9]*%' | tr -d ':' | tr '\n' ',' | tr -d '%' | sed 's/ $//')
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        VPU_USAGE=$(cat /proc/soph/vpuinfo | tr -d '\n' | grep -ao ':[0-9]*%' | tr -d ':' | tr '\n' ',' | tr -d '%' | sed 's/ $//')
    fi
fi

# DEVICE_MEM_USAGE
TPU_MEM_USAGE="0"
VPU_MEM_USAGE="0"
VPP_MEM_USAGE="0"
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        TPU_MEM_USAGE=$(get_ion_usage "/sys/kernel/debug/ion/bm_npu_heap_dump")
        VPU_MEM_USAGE=$(get_ion_usage "/sys/kernel/debug/ion/bm_vpu_heap_dump")
        VPP_MEM_USAGE=$(get_ion_usage "/sys/kernel/debug/ion/bm_vpp_heap_dump")
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        TPU_MEM_USAGE=$(get_ion_usage "/sys/kernel/debug/ion/cvi_npu_heap_dump")
        VPP_MEM_USAGE=$(get_ion_usage "/sys/kernel/debug/ion/cvi_vpp_heap_dump")
    fi
fi

# BOARD_TYPE
BOARD_TYPE=""
MCU_VERSION=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        BOARD_TYPE=$(grep "board type" /sys/class/i2c-dev/i2c-1/device/1-0017/information 2>/dev/null | awk -F'"' '{print $4}' 2>/dev/null)
        MCU_VERSION=$(grep "mcu version" /sys/class/i2c-dev/i2c-1/device/1-0017/information 2>/dev/null | awk -F'"' '{print $4}' 2>/dev/null)
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        mcu_reg=$(busybox devmem 0x05026024 2>/dev/null)
        mcu_1=$(( (mcu_reg & 0xFF0000) >> 16 ))
        mcu_2=$(( (mcu_reg & 0xFF00) >> 8 ))
        mcu_3=$(( (mcu_reg & 0xFF) >> 0 ))
        MCU_VERSION="$mcu_1"."$mcu_2"."$mcu_3"
    fi
fi

# KERNEL_VERSION
KERNEL_VERSION="$(uname -r)"
KERNEL_BUILD_TIME="$(uname -v)"

# SYSTEM_TYPE
SYSTEM_TYPE=$(head -n 1 /etc/issue 2>/dev/null | sed 's| \\n||g' | sed 's| \\l||g')

# DOCKER_VERSION
DOCKER_VERSION=$(docker --version 2>/dev/null | sed 's| \\n||g')

# MMC0_CID
if [[ "${WORK_MODE}" == "SOC" ]]; then
    MMC0_CID=$(cat /sys/class/mmc_host/mmc0/mmc0\:0001/cid 2>/dev/null | sed 's| \\n||g')
fi

# DISK_INFO
DISK_INFO=$(df -T | grep ^/dev | awk '{printf "%s%s:%s", (NR==1 ? "" : " "), $7, $6} END {print ""}')

# SDK_VERSION
SDK_VERSION=""
LIBSOPHON_VERSION=""
SOPHON_MEDIA_VERSION=""
if [[ "${WORK_MODE}" == "SOC" ]]; then
    if [[ "${CPU_MODEL}" == "bm1684x" ]] || [[ "${CPU_MODEL}" == "bm1684" ]]; then
        if [[ "${KERNEL_VERSION}" == "5.4."* ]]; then
            SDK_VERSION=$(/usr/sbin/bm_version 2>/dev/null | grep "SophonSDK version" | sed 's|SophonSDK version: ||g')
            LIBSOPHON_VERSION=$(readlink /opt/sophon/libsophon-current 2>/dev/null | awk -F'-' '{print $2}')
            SOPHON_MEDIA_VERSION=$(readlink /opt/sophon/sophon-ffmpeg-latest 2>/dev/null | awk -F'_' '{print $2}')
        elif [[ "${KERNEL_VERSION}" == "4.9."* ]]; then
            SDK_VERSION=$(grep "VERSION" /system/data/buildinfo.txt 2>/dev/null | awk '{print $2}')
        fi
    elif [[ "${CPU_MODEL}" == "bm1688" ]] || [[ "${CPU_MODEL}" == "cv186ah" ]]; then
        SDK_VERSION=$(/usr/sbin/bm_version 2>/dev/null | grep "Gemini_SDK" | sed 's|Gemini_SDK: ||g')
        LIBSOPHON_VERSION=$(readlink /opt/sophon/libsophon-current 2>/dev/null | awk -F'-' '{print $2}')
        SOPHON_MEDIA_VERSION=$(readlink /opt/sophon/sophon-ffmpeg-latest 2>/dev/null | awk -F'_' '{print $2}')
    fi
else
    DRIVER_RELEASE_VERSION=$(cat /proc/bmsophon/driver_version 2>/dev/null | awk -F':' '{print $2}' | awk '{print $1}')
    DRIVER_RELEASE_TIME=$(cat /proc/bmsophon/driver_version 2>/dev/null | awk -F':' '{print $3}' | awk '{print $1}')
    LIBSOPHON_VERSION=$(readlink /opt/sophon/libsophon-current 2>/dev/null | awk -F'-' '{print $2}')
    SOPHON_MEDIA_VERSION=$(readlink /opt/sophon/sophon-ffmpeg-latest 2>/dev/null | awk -F'_' '{print $2}')
fi

# PCIE_INFO
CARD_NUM=""
CHIP_NUM=""
if [[ "${WORK_MODE}" == "PCIE" ]]; then
    CARD_NUM=$(cat /proc/bmsophon/card_num)
    CHIP_NUM=$(cat /proc/bmsophon/chip_num)
    for i in $(seq 0 $((CARD_NUM - 1))); do
        eval "CARD${i}_TYPE='$(cat /proc/bmsophon/card${i}/board_type)'"
        eval "CARD${i}_CHIP_ID='$(cat /proc/bmsophon/card${i}/bmsophon*/tpuid | sort -n | tr '\n' ' ' | sed 's/ *$//')'"
        eval "CARD${i}_CHIP_NUM='$(cat /proc/bmsophon/card${i}/chip_num_on_card)'"
        eval "CARD${i}_CHIP_TYPE='$(cat /proc/bmsophon/card${i}/chipid)'"
        eval "CARD${i}_SN='$(cat /proc/bmsophon/card${i}/sn)'"
        eval "CARD${i}_POWER='$(cat /proc/bmsophon/card${i}/board_power | awk '{print $1}')'"
        eval "CARD${i}_TEMP='$(cat /proc/bmsophon/card${i}/board_temp | awk '{print $1}')'"
        eval "CARD${i}_BOARD_VERSION='$(cat /proc/bmsophon/card${i}/board_version)'"
        eval "CARD_CHIP_ID=$(echo \"\$CARD${i}_CHIP_ID\")"
        eval "CARD${i}_CHIP_DDR_SIZE=''"
        eval "CARD${i}_CHIP_POWER=''"
        eval "CARD${i}_CHIP_TEMP=''"
        eval "CARD${i}_TPU_FREQ=''"
        eval "CARD${i}_TPU_USAGE=''"
        eval "CARD${i}_VPU_USAGE=''"
        for k in ${CARD_CHIP_ID}; do
            eval "CARD${i}_CHIP_DDR_SIZE+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/ddr_capacity | tr -d 'g' | awk '{print $NF}') '"
            eval "CARD${i}_CHIP_HEAP_SIZE+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/heap | awk '{print $4}' | tr -d ',' | while read -r hex; do decimal=$(printf "%d" $hex); echo "scale=0; $decimal / 1024 / 1024" | bc; done | tr '\n' ',' | sed 's/,$//') '"
            eval "CARD${i}_CHIP_POWER+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/chip_power | awk '{print $1}') '"
            eval "CARD${i}_CHIP_TEMP+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/chip_temp | awk '{print $1}') '"
            eval "CARD${i}_TPU_FREQ+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/clk | grep ^tpu: | awk '{print $2}') '"
            eval "CARD${i}_VPU_FREQ+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/clk | grep ^vpu: | awk '{print $2}') '"
            eval "CARD${i}_DDR_FREQ+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/clk | grep ^ddr: | awk '{print $2}') '"
            eval "CARD${i}_TPU_USAGE+='$(cat /sys/class/bm-sophon/bm-sophon${k}/device/npu_usage | awk -F':' '{print $2}' | awk '{print $1}') '"
            eval "CARD${i}_VPU_USAGE+='$(cat /proc/bmsophon/card${i}/bmsophon${k}/media | tr -d '\n' | grep -ao ':[0-9]*%' | tr -d ':' | tr '\n' ',' | tr -d '%' | sed 's/,$//'; echo ' ')'"
        done
        eval "CARD${i}_CHIP_DDR_SIZE=\$(echo \$CARD${i}_CHIP_DDR_SIZE | sed 's/ *$//')"
        eval "CARD${i}_CHIP_HEAP_SIZE=\$(echo \$CARD${i}_CHIP_HEAP_SIZE | sed 's/ *$//')"
        eval "CARD${i}_CHIP_POWER=\$(echo \$CARD${i}_CHIP_POWER | sed 's/ *$//')"
        eval "CARD${i}_CHIP_TEMP=\$(echo \$CARD${i}_CHIP_TEMP | sed 's/ *$//')"
        eval "CARD${i}_TPU_FREQ=\$(echo \$CARD${i}_TPU_FREQ | sed 's/ *$//')"
        eval "CARD${i}_VPU_FREQ=\$(echo \$CARD${i}_VPU_FREQ | sed 's/ *$//')"
        eval "CARD${i}_DDR_FREQ=\$(echo \$CARD${i}_DDR_FREQ | sed 's/ *$//')"
        eval "CARD${i}_TPU_USAGE=\$(echo \$CARD${i}_TPU_USAGE | sed 's/ *$//')"
        eval "CARD${i}_VPU_USAGE=\$(echo \$CARD${i}_VPU_USAGE | sed 's/ *$//')"
    done
fi

# del temp file
rm -f "$temp_file"

# VIEW INFO
if [[ "${WORK_MODE}" == "SOC" ]]; then
	echo "BOOT_TIME(s)|${BOOT_TIME}|"
	echo "DATE_TIME|${DATE_TIME}|"
    echo "WORK_MODE|${WORK_MODE}|"
    echo "CPU_MODEL|${CPU_MODEL}|"
    echo "DDR_SIZE(MiB)|${DDR_SIZE}|"
    echo "EMMC_SIZE(MiB)|${EMMC_SIZE}|"
    echo "SYSTEM_MEM(MiB)|${SYSTEM_MEM}|"
    echo "TPU_MEM(MiB)|${TPU_MEM}|"
    echo "VPU_MEM(MiB)|${VPU_MEM}|"
    echo "VPP_MEM(MiB)|${VPP_MEM}|"
    echo "TPU_MEM_USAGE(%)|${TPU_MEM_USAGE}|"
    echo "VPU_MEM_USAGE(%)|${VPU_MEM_USAGE}|"
    echo "VPP_MEM_USAGE(%)|${VPP_MEM_USAGE}|"
    echo "CPU_ALL_USAGE(%)|${CPU_ALL_USAGE}|"
    echo "CPUS_USAGE(%)|${CPUS_USAGE}|"
    echo "SYSTEM_MEM_USAGE(%)|${SYSTEM_MEM_USAGE}|"
    echo "DTS_NAME|${DTS_NAME}|"
    echo "DEVICE_MODEL|${DEVICE_MODEL}|"
    echo "CPU_CLK(Hz)|${CPU_CLK}|"
    echo "TPU_CLK(Hz)|${TPU_CLK}|"
    echo "VPU_CLK(Hz)|${VPU_CLK}|"
    echo "CHIP_SN|${CHIP_SN}|"
    echo "DEVICE_SN|${DEVICE_SN}|"
    echo "ETH0_MAC|${ETH0_MAC}|"
    echo "ETH1_MAC|${ETH1_MAC}|"
    echo "CHIP_TEMP(degree Celsius)|${CHIP_TEMP}|"
    echo "TPU_USAGE(%)|${TPU_USAGE}|"
    echo "BOARD_TYPE|${BOARD_TYPE}|"
    echo "MCU_VERSION|${MCU_VERSION}|"
    echo "KERNEL_VERSION|${KERNEL_VERSION}|"
    echo "KERNEL_BUILD_TIME|${KERNEL_BUILD_TIME}|"
    echo "SYSTEM_TYPE|${SYSTEM_TYPE}|"
    echo "DOCKER_VERSION|${DOCKER_VERSION}|"
    echo "MMC0_CID|${MMC0_CID}|"
    echo "DISK_INFO|${DISK_INFO}|"
    echo "SDK_VERSION|${SDK_VERSION}|"
    echo "LIBSOPHON_VERSION|${LIBSOPHON_VERSION}|"
    echo "SOPHON_MEDIA_VERSION|${SOPHON_MEDIA_VERSION}|"
else
	echo "BOOT_TIME(s)|${BOOT_TIME}|"
	echo "DATE_TIME|${DATE_TIME}|"
    echo "WORK_MODE|${WORK_MODE}|"
    echo "CARD_NUM|${CARD_NUM}|"
    echo "CHIP_NUM|${CHIP_NUM}|"
    for i in $(seq 0 $((CARD_NUM - 1))); do
        eval "echo \"CARD${i}_TYPE|\$CARD${i}_TYPE|\""
        eval "echo \"CARD${i}_CHIP_ID|\$CARD${i}_CHIP_ID|\""
        eval "echo \"CARD${i}_CHIP_NUM|\$CARD${i}_CHIP_NUM|\""
        eval "echo \"CARD${i}_CHIP_TYPE|\$CARD${i}_CHIP_TYPE|\""
        eval "echo \"CARD${i}_SN|\$CARD${i}_SN|\""
        eval "echo \"CARD${i}_POWER(W)|\$CARD${i}_POWER|\""
        eval "echo \"CARD${i}_TEMP(degree Celsius)|\$CARD${i}_TEMP|\""
        eval "echo \"CARD${i}_CHIP_DDR_SIZE(GiB)|\$CARD${i}_CHIP_DDR_SIZE|\""
        eval "echo \"CARD${i}_CHIP_HEAP_SIZE(MiB)|\$CARD${i}_CHIP_HEAP_SIZE|\""
        eval "echo \"CARD${i}_CHIP_POWER(W)|\$CARD${i}_CHIP_POWER|\""
        eval "echo \"CARD${i}_CHIP_TEMP(degree Celsius)|\$CARD${i}_CHIP_TEMP|\""
        eval "echo \"CARD${i}_TPU_FREQ(MHz)|\$CARD${i}_TPU_FREQ|\""
        eval "echo \"CARD${i}_VPU_FREQ(MHz)|\$CARD${i}_VPU_FREQ|\""
        eval "echo \"CARD${i}_DDR_FREQ(MHz)|\$CARD${i}_DDR_FREQ|\""
        eval "echo \"CARD${i}_TPU_USAGE(%)|\$CARD${i}_TPU_USAGE|\""
        eval "echo \"CARD${i}_VPU_USAGE(%)|\$CARD${i}_VPU_USAGE|\""
    done
    echo "DRIVER_RELEASE_VERSION|${DRIVER_RELEASE_VERSION}|"
    echo "DRIVER_RELEASE_TIME|${DRIVER_RELEASE_TIME}|"
    echo "LIBSOPHON_VERSION|${LIBSOPHON_VERSION}|"
    echo "SOPHON_MEDIA_VERSION|${SOPHON_MEDIA_VERSION}|"
    echo "KERNEL_BUILD_TIME|${KERNEL_BUILD_TIME}|"
    echo "SYSTEM_TYPE|${SYSTEM_TYPE}|"
    echo "DISK_INFO|${DISK_INFO}|"
    echo "CPU_ALL_USAGE(%)|${CPU_ALL_USAGE}|"
    echo "CPUS_USAGE(%)|${CPUS_USAGE}|"
    echo "SYSTEM_MEM_USAGE(%)|${SYSTEM_MEM_USAGE}|"
fi

