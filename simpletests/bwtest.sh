# first need to "sudo iperf3 -s" on the target server 
iperf3 -c 172.31.51.133 -P 1 -i 5 -t 3600 -V | grep Mbits | head -n -2 | awk '{print $7}' > trace133.log
iperf3 -c 172.31.50.34 -P 1 -i 5 -t 3600 -V | grep Mbits | head -n -2 | awk '{print $7}' > trace34.log