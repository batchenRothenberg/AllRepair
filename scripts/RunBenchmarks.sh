#!/bin/bash

# Reproduce TCAS experiments
# mutation level 1
./AllRepair.sh Benchmarks/Tcas -m 1 -t 600 -s 2 2>&1 | ./ParseResults.sh
# mutation level 2
./AllRepair.sh Benchmarks/Tcas -m 2 -t 600 -s 2 2>&1 | ./ParseResults.sh

# Reroduce Qlose experiments
# mutation level 1, increasing bounds 
./AllRepair.sh Benchmarks/Qlose/loops -m 1 -u 1 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 1 -u 2 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 1 -u 5 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 1 -u 10 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 1 -u 15 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 1 -u 1 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 1 -u 2 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 1 -u 5 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 1 -u 10 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 1 -u 15 -t 600 -s 2 2>&1 | ./ParseResults.sh
# mutation level 2, increasing bounds 
./AllRepair.sh Benchmarks/Qlose/loops -m 2 -u 1 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 2 -u 2 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 2 -u 5 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 2 -u 10 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops -m 2 -u 15 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 2 -u 1 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 2 -u 2 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 2 -u 5 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 2 -u 10 -t 600 -s 2 2>&1 | ./ParseResults.sh
./AllRepair.sh Benchmarks/Qlose/loops_with_two -m 2 -u 15 -t 600 -s 2 2>&1 | ./ParseResults.sh
