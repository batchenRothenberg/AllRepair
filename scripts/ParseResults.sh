#!/bin/bash

results_dir="AllRepairResults"
separating_string="___________________"
declare -a column_keys=( "filename" "hard" "soft" "programs" "translation" "repair" "numrepairs" "totaltofirst" "translationtime" "timetofirst" "maxinspected"  "satchecktotal" "satblocktotal" "smttotal" "setuptotal" "total" "smtcount" "smtper" )
declare -A column_titles=( ["filename"]="file name" ["hard"]="hard constraints" ["soft"]="max mutation size" ["programs"]="mutated programs" ["translation"]="translation result" ["repair"]="repair result" ["numrepairs"]="found repairs" ["timetofirst"]="time to first repair [s]" ["maxinspected"]="max inspected size" ["satchecktotal"]="sat check [s]" ["satblocktotal"]="sat block [s]" ["smttotal"]="smt check [s]" ["setuptotal"]="setup [s]" ["smtcount"]="smt check count" ["total"]="total repair time [s]" ["translationtime"]="translation time [s]" ["totaltofirst"]="total time to first repair" ["smtper"]="SMT check per" )
declare -A prefix_strings=( ["filename"]="Repairing file " ["hard"]="Hard constraints (group 0): " ["soft"]="Max mutation size: " ["programs"]="Mutated programs in search space: " ["maxinspected"]="Max inspected size: " ["satchecktotal"]="SAT check : " ["satblocktotal"]="SAT block : " ["smttotal"]="SMT check : " ["setuptotal"]="setup : " ["total"]="total : " ["smtcount"]="SMT check count :" ["translationtime"]="AllRepair: Translation duration: " ["smtper"]="SMT check per :" )
declare -A current_row
in_repair_scope=0 # boolean


main() {
	# Determine output directory (default or $1)
	if ! [ -z "$1" ]; then
		results_dir=$1	
	fi
	
	# Create output directory
	if ! [ -d "$results_dir" ]; then
		mkdir "$results_dir"
	fi

	# Determine filenames
	read settings_string # Read settings from first input line to include in file name
	echo "$settings_string" # output of AllRepair should look the same
	parse_settings "$settings_string"
	current_date=`date +'%d_%m_%Y_%H_%M_%S'`
	settings_to_filename="${mutation_level:+m${mutation_level}_}${unwinding_bound:+u${unwinding_bound}_}${timeout:+t${timeout}_}${repair_limit:+r${repair_limit}_}${size_limit:+s${size_limit}_}${program_limit:+p${program_limit}_}"
	results_filename="$results_dir/AllRepair_results_$settings_to_filename$current_date.csv"
	repairs_filename="$results_dir/AllRepair_repairs_$settings_to_filename$current_date"
	
	# Print date, time and settings (overwrites existing content!)
	echo "$current_date" > $results_filename
	echo "$current_date" > $repairs_filename
	echo "$settings_string" >> $results_filename
	echo "$settings_string" >> $repairs_filename


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
		initialize_repair_scope "$line"
		check_prefix_strings "$line"
		check_translation_result "$line"
		check_repair_result "$line"
		update_repair_scope_and_separate_files "$line"
		update_repair_count "$line"
		save_repair "$line" # must come after update_repair_scope_and_separate_files
		check_time_to_first_repair "$line" # must come after update_repair_count
		echo $line
	done
	
	# Print end time
	echo `date +'%d_%m_%Y_%H_%M_%S'` >> $results_filename
	echo `date +'%d_%m_%Y_%H_%M_%S'` >> $repairs_filename
}

parse_settings () {
	if echo "$1" | grep -q ".*Mutation level=.*"; then
		mutation_level=`echo "$1" | sed 's/.*Mutation level=\([0-9]*\).*/\1/'`
	fi
	if echo "$1" | grep -q ".*Unwinding bound=.*"; then
		unwinding_bound=`echo "$1" | sed 's/.*Unwinding bound=\([0-9]*\).*/\1/'`
	fi
	if echo "$1" | grep -q ".*Timeout=.*"; then
		timeout=`echo "$1" | sed 's/.*Timeout=\([0-9]*\).*/\1/'`
	fi
	if echo "$1" | grep -q ".*Max repairs to find=.*"; then
		repair_limit=`echo "$1" | sed 's/.*Max repairs to find=\([0-9]*\).*/\1/'`
	fi
	if echo "$1" | grep -q ".*Max repair size=.*"; then
		size_limit=`echo "$1" | sed 's/.*Max repair size=\([0-9]*\).*/\1/'`
	fi
	if echo "$1" | grep -q ".*Max programs to check=.*"; then
		program_limit=`echo "$1" | sed 's/.*Max programs to check=\([0-9]*\).*/\1/'`
	fi
}

initialize_repair_scope () {
	if [[ "$1" == "Repairing file "* ]]; then
		in_repair_scope=0
	fi
}

update_repair_scope_and_separate_files () {
	if [[ "$1" == "-------------"* ]]; then
		# if first repair- print line to separate this file for previous files
		if [ ${current_row["numrepairs"]} -eq 0 ]; then
			echo "__________________________________________________________________________" >> $repairs_filename
		fi 
		in_repair_scope=$((1-in_repair_scope))
	fi
}

save_repair () {
	if ((in_repair_scope)); then
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

update_repair_count () {
	if [[ $1 == "Possible repair:" ]]; then
		let current_row["numrepairs"]+=1
	fi
}

check_repair_result () {
	if [[ $1 == "AllRepair: SEARCH SPACE COVERED SUCCESSFULLY" ]]; then
		current_row["repair"]="FULL COVERAGE"
	elif [[ $1 == "AllRepair: TIMEOUT" ]]; then
		current_row["repair"]="TIMEOUT"
	elif [[ $1 == "AllRepair: REQUESTED NUMBER OF REPAIRS FOUND" ]]; then
		current_row["repair"]="REPAIR LIMIT"
	elif [[ $1 == "AllRepair: MAX NUMBER OF MUTATED PROGRAMS INSPECTED" ]]; then
		current_row["repair"]="PROGRAM LIMIT"
	elif [[ $1 == "AllRepair: MAX MUTATION SIZE REACHED" ]]; then
		current_row["repair"]="SIZE LIMIT"
	elif [[ $1 == "AllRepair: EXTERNALLY TERMINATED" ]]; then
		current_row["repair"]="TERMINATED"
	elif [[ $1 == "AllRepair: INTERRUPTED" ]]; then
		current_row["repair"]="INTERRUPTED"
	elif [[ $1 == "AllRepair: ORIGINAL PROGRAM IS CORRECT" ]]; then
		current_row["repair"]="ORIGINAL CORRECT"
	else
		current_row["repair"]="ERROR"
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

