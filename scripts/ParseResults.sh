#!/bin/bash

results_dir="AllRepairResults"
separating_string="___________________"
declare -a column_keys=( "filename" "hard" "soft" "programs" "translation" "repair" "numrepairs" "timetofirst" "maxinspected" "satchecktotal" "satblocktotal" "smttotal" "setuptotal" "total" "smtcount" "translationtime" "totaltofirst" )
declare -A column_titles=( ["filename"]="file name" ["hard"]="hard constraints" ["soft"]="max mutation size" ["programs"]="mutated programs" ["translation"]="translation result" ["repair"]="repair result" ["numrepairs"]="found repairs" ["timetofirst"]="time to first repair [s]" ["maxinspected"]="max inspected size" ["satchecktotal"]="sat check [s]" ["satblocktotal"]="sat block [s]" ["smttotal"]="smt check [s]" ["setuptotal"]="setup [s]" ["smtcount"]="smt check count" ["total"]="total repair time [s]" ["translationtime"]="translation time [s]" ["totaltofirst"]="total time to first repair" )
declare -A prefix_strings=( ["filename"]="Repairing file " ["hard"]="Hard constraints (group 0): " ["soft"]="Max mutation size: " ["programs"]="Mutated programs in search space: " ["maxinspected"]="Max inspected size: " ["satchecktotal"]="SAT check : " ["satblocktotal"]="SAT block : " ["smttotal"]="SMT check : " ["setuptotal"]="setup : " ["total"]="total : " ["smtcount"]="SMT check count :" ["translationtime"]="AllRepair: Translation duration: " )
declare -A current_row

main() {
	# Determine output files: $1 for results table, $2 for list of found repairs
	if [ -z "$1" ]; then
		if ! [ -d "$results_dir" ]; then
			mkdir "$results_dir"
		fi
		results_filename="$results_dir/AllRepair_results_"`date +'%d_%m_%Y_%X'`
	else
		results_filename="$1"
	fi
	if [ -z "$2" ]; then
		if ! [ -d "$results_dir" ]; then
			mkdir "$results_dir"
		fi
		repairs_filename="$results_dir/AllRepair_repairs"`date +'%d_%m_%Y_%X'`
	else
		repairs_filename="$2"
	fi

	# Print date and time (overwrites existing content!)
	echo `date +'%d_%m_%Y_%X'` > $results_filename
	echo `date +'%d_%m_%Y_%X'` > $repairs_filename

	# Read settings from first input line and print them
	read line
	echo "$line" >> $results_filename
	echo "$line" # output of AllRepair should look the same

	# Print title 
	for key in "${column_keys[@]}"; do 
		echo -n "${column_titles[$key]}," >> $results_filename
	done
	echo "" >> $results_filename

	# Parse input stream (from AllRepair) and add to output
	current_row["numrepairs"]=0
	while read line; do
		if [[ $line == "${separating_string}"* ]]; then
			# Finished repairing file - print current_row
			calculate_total_time_to_first_Repair
			for key in "${column_keys[@]}"; do 
		    		echo -n "${current_row[$key]}," >> $results_filename
			done
			echo "" >> $results_filename
			# Initialize current_row array
			unset current_row
			declare -A current_row
			current_row["numrepairs"]=0
		fi
		check_prefix_strings "$line"
		check_translation_result "$line"
		check_repair_result "$line"
		check_repair_found "$line"
		save_repair "$line"
		check_time_to_first_repair "$line"
		echo $line
	done
	
	# Print end time
	echo `date +'%d_%m_%Y_%X'` >> $results_filename
	echo `date +'%d_%m_%Y_%X'` >> $repairs_filename
}

save_repair () {
	if [[ "$1" == "Elapsed time: "* ]] || [[ "$1" == "In file "* ]] || [[ "$1" == "Replace "* ]]; then
		echo "$1" >> $repairs_filename	
	fi
}

calculate_total_time_to_first_Repair () {
	if [[ ! -z "${current_row["timetofirst"]}" ]]; then
		current_row["totaltofirst"]=`echo "${current_row["translationtime"]:-0} + ${current_row["timetofirst"]}" | bc`
	fi
}

check_time_to_first_repair () {
	if [ ${current_row["numrepairs"]} -eq 1 ]; then
		check_prefix_string_and_save "$1" "Elapsed time: " "timetofirst"
	fi
}

check_repair_found () {
	if [[ $1 == "Possible solution:" ]]; then
		let current_row["numrepairs"]+=1
		# if first repair- print line to separate this file for previous files
		if [ ${current_row["numrepairs"]} -eq 1 ]; then
			echo "_________________________________________________" >> $repairs_filename
		fi
	fi
}

check_repair_result () {
	if [[ $1 == "AllRepair: REPAIR PROCESS TERMINATED SUCCESSFULLY" ]]; then
		current_row["repair"]="SUCCESS"
	elif [[ $1 == "AllRepair: ERROR DURING REPAIR" ]]; then
		current_row["repair"]="FAILURE"
	fi
}

check_translation_result () {
	if [[ $1 == "AllRepair: TRANSLATION PROCESS TERMINATED SUCCESSFULLY" ]]; then
		current_row["translation"]="SUCCESS"
	elif [[ $1 == "AllRepair: ERROR DURING TRANSLATION" ]]; then
		current_row["translation"]="FAILURE"
	fi
}

check_prefix_strings () {
	for key in "${!prefix_strings[@]}"; do 
		identifying_string=${prefix_strings[$key]}
		check_prefix_string_and_save "${1}" "${identifying_string}" "${key}"
	done
}

check_prefix_string_and_save () {
	if [[ "$1" == "$2"* ]]; then
		info=${1#"$2"}
		current_row[$3]=$info
	fi
}

main "$@"

