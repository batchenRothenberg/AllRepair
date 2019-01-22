#!/bin/bash

results_dir="AllRepairResults"
# Order in column_titles and column_identifying_texts must be the same, and determines column order in output.
declare -a column_titles=( "file name" "mutated programs" "constraints" )
declare -a column_identifying_texts=( "Repairing file " "Total number of mutated programs: " "Total number of constraints: " )
declare -a current_row

# Determine output file
if [ -z "$1" ]; then
	if ! [ -d "$results_dir" ]; then
		mkdir "$results_dir"
	fi
	results_filename="$results_dir/AllRepair_results_"`date +'%d_%m_%Y_%X'`
else
	results_filename="$1"
fi

# Print date and time (overwrites existing content!)
echo `date +'%d_%m_%Y_%X'` > $results_filename

# Print title 
for column in "${column_titles[@]}"; do 
	echo -n "${column}," >> $results_filename
done
echo "" >> $results_filename

# Parse input stream (from AllRepair) and add to output
while read line; do
	for index in "${!column_identifying_texts[@]}"; do 
		identifying_string=${column_identifying_texts[$index]}
		if [[ $line == "$identifying_string"* ]]; then
			echo "match found"
			info=${line#"$identifying_string"}
			current_row[$index]=$info
		fi
	done
done

for data in "${current_row[@]}"; do 
	echo -n "${data}," >> $results_filename
done
echo "" >> $results_filename

