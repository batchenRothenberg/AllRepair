#!/bin/bash

results_dir="AllRepairResults"
separating_string="___________________"
declare -a column_keys=( "filename" "hard" "soft" "programs" "translation" "repair" "numrepairs")
declare -A column_titles=( ["filename"]="file name" ["hard"]="hard constraints" ["soft"]="max mutation size" ["programs"]="mutated programs" ["translation"]="translation result" ["repair"]="repair result" ["numrepairs"]="found repairs" )
declare -A prefix_strings=( ["filename"]="Repairing file " ["hard"]="Hard constraints (group 0): " ["soft"]="Max mutation size: " ["programs"]="Mutated programs in search space: " )
declare -A current_row

main() {
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
	for key in "${column_keys[@]}"; do 
		echo -n "${column_titles[$key]}," >> $results_filename
	done
	echo "" >> $results_filename

	# Parse input stream (from AllRepair) and add to output
	while read line; do
		if [[ $line == "${separating_string}"* ]]; then
			# Finished repairing file - print current_row
			for key in "${column_keys[@]}"; do 
		    		echo -n "${current_row[$key]}," >> $results_filename
			done
			echo "" >> $results_filename
			# Initialize current_row array
			unset current_row
			declare -A current_row
		fi
		check_prefix_strings "$line"
		check_translation "$line"
		check_repair "$line"
		echo $line
	done
}

check_repair () {
	if [[ $1 == "AllRepair: REPAIR PROCESS TERMINATED SUCCESSFULLY" ]]; then
		current_row["repair"]="SUCCESS"
	elif [[ $1 == "AllRepair: ERROR DURING REPAIR" ]]; then
		current_row["repair"]="FAILURE"
	fi
}

check_translation () {
	if [[ $1 == "AllRepair: TRANSLATION PROCESS TERMINATED SUCCESSFULLY" ]]; then
		current_row["translation"]="SUCCESS"
	elif [[ $1 == "AllRepair: ERROR DURING TRANSLATION" ]]; then
		current_row["translation"]="FAILURE"
	fi
}

check_prefix_strings () {
	for key in "${!prefix_strings[@]}"; do 
		identifying_string=${prefix_strings[$key]}
		check_prefix_string_and_save "$1" "${identifying_string}" "${key}"
	done
}

check_prefix_string_and_save () {
	if [[ $1 == "$2"* ]]; then
		info=${1#"$2"}
		current_row[$3]=$info
	fi
}

main "$@"

