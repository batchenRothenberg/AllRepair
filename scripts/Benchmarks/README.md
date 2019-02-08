# Reproducing AllRepair experiments

Our experiments on the TCAS and QLOSE benchmarks were run by simply running the AllRepair script with the appropriate arguments and passing the output to the ParseResults script.
To reproduce all of our experiments, return to the scripts directory and run (this might take a while..)
    
    ./RunBenchmarks.sh
    
You will find the results under scripts/AllRepairResults.

To reproduce the results of a single experiment, open the RunBenchmarks script, select individual experiments that you would like to repeat, and run these commands in the terminal from the scripts directory.

Folder all_results in the current directory contains the output files we have recieved from the script in our experiments, for comparison.
The file Qlose_results_summary.xlsx was produced manually and combines all csv files into a single excel table.
All statistics reported in the paper were produced manually in excel using this file.


