#!/bin/bash

results_dir="AllRepairResults"
declare -a column_titles=( "file name" "constraints" "mutated programs" )
declare -a column_identifying_texts=( "Repairing file " "Total number of constraints: " "Total number of mutated programs: " )

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
	for identifying_string in "${column_identifying_texts[@]}"; do 
		if [[ $line == "$identifying_string"* ]]; then
			echo "match found"
			info=${line#"$identifying_string"}
			echo -n "$info," >> $results_filename
		fi
	done
done
