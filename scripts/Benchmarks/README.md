# Reproducing AllRepair experiments

Our experiments on the TCAS and QLOSE benchmarks were run by simply running the AllRepair script with the appropriate arguments and passing the output to the ParseResults script.
To reproduce all of our experiments, run the script in this directory (this make take a while..)
    
    ./RunBenchmarks.sh
    
To reproduce the results of a single experiment, open the RunBenchmarks script, select individual experiments that you would like to repeat, and run these commands in the terminal.

Folder all_results in this directory contains the output files we have recieved from the script in our experiments, for comparison.
The file Qlose_results_summary.xlsx was produced manually and combines all csv files into a single excel table.
All statistics reported in the paper were produced manually in excel using this file.


