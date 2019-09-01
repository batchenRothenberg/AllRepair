#!/bin/bash

SETTINGS_PREFIX="AllRepair: SETTINGS:"
REPAIR_INIT_STRING="_______________________________________________________________________________"
separating_string="___________________"
declare -a column_keys=( "filename" "hard" "soft" "programs" "translation" "repair" "numrepairs" "totaltofirst" "translationtime" "timetofirst" "maxinspected"  "satchecktotal" "satblocktotal" "smttotal" "setuptotal" "total" "smtcount" "smtper" "mutlevel" "bound" "timeout" "replimit" "sizelimit" "proglimit" "incremental" "block" "bounds" "pointer" "memory" "divby" "function" "nomut" )
declare -a setting_keys=( "mutlevel" "bound" "timeout" "replimit" "sizelimit" "proglimit" "incremental" "block" "bounds" "pointer" "memory" "divby" "function" "nomut" )
declare -A column_titles=( ["filename"]="file name" ["hard"]="hard constraints" ["soft"]="max mutation size" ["programs"]="mutated programs" ["translation"]="translation result" ["repair"]="repair result" ["numrepairs"]="found repairs" ["timetofirst"]="time to first repair [s]" ["maxinspected"]="max inspected size" ["satchecktotal"]="sat check [s]" ["satblocktotal"]="sat block [s]" ["smttotal"]="smt check [s]" ["setuptotal"]="setup [s]" ["smtcount"]="smt check count" ["total"]="total repair time [s]" ["translationtime"]="translation time [s]" ["totaltofirst"]="total time to first repair" ["smtper"]="SMT check per" ["mutlevel"]="mutation level" ["bound"]="unwinding bound" ["timeout"]="timeout" ["replimit"]="repair limit" ["sizelimit"]="size limit" ["proglimit"]="program limit" ["incremental"]="SMT incremental method" ["block"]="blocking method" ["bounds"]="array bounds check" ["pointer"]="pointer check" ["memory"]="memory leak check" ["divby"]="div by 0 check" ["function"]="starting function" ["nomut"]="no-mutation functions" )
declare -A prefix_strings=( ["filename"]="Repairing file " ["hard"]="Hard constraints (group 0): " ["soft"]="Max mutation size: " ["programs"]="Mutated programs in search space: " ["maxinspected"]="Max inspected size: " ["satchecktotal"]="SAT check : " ["satblocktotal"]="SAT block : " ["smttotal"]="SMT check : " ["setuptotal"]="Setup : " ["readgsmt2total"]="Parse gsmt2 : " ["total"]="total : " ["smtcount"]="SMT check count :" ["translationtime"]="AllRepair: Translation duration: " ["smtper"]="SMT check per :" ["mutlevel"]="Mutation level=" ["bound"]="Unwinding bound=" ["timeout"]="Timeout=" ["replimit"]="Max repairs to find=" ["sizelimit"]="Max repair size=" ["proglimit"]="Max programs to check=" ["incremental"]="SMT incremental method=" ["block"]="Blocking method=" ["bounds"]="Array out of bounds check: " ["pointer"]="Pointer check: " ["memory"]="Memory leak check: " ["divby"]="Div by 0 check: " ["function"]="Function to repair=" ["nomut"]="Functions to avoid mutating=") #"builtin"
declare -A current_row
in_repair_scope=0 # boolean

main () {
	results_filename="$1"
	repairs_filename="$2"
	if (( $# != 2 )); then
		echo "expecting two arguments, $# were given"
		exit 1
	fi
	create_files_if_dont_exist "$results_filename" "$repairs_filename"
	make_csv_title_if_necessary "$results_filename"
	parse_data
}

create_files_if_dont_exist () {
  	mkdir -p "$( dirname "$1" )"
  	touch "$1"
	mkdir -p "$( dirname "$2" )"
  	touch "$2"
}

make_csv_title_if_necessary () {
	if [[ ! -s "$1" ]]; then
		make_title
		echo "$TITLE" >> "$1"
	fi
}

make_title () {
	for key in "${column_keys[@]}"; do 
		TITLE+="${column_titles[$key]},"
	done
}

parse_data () {
	current_row["numrepairs"]=0
	while read line; do
		if [[ $line == "${separating_string}"* ]]; then
			# Finished repairing file - print current_row
			calculate_total_time_to_first_Repair
			for key in "${column_keys[@]}"; do 
		    		echo -n "${current_row[$key]}," >> "$results_filename"
			done
			echo "" >> $results_filename
			# Initialize current_row array
			unset current_row
			declare -A current_row
			current_row["numrepairs"]=0
		fi
		initialize_repair_scope "$line"
		initialize_settings_printing "$line"
		check_prefix_strings "$line"
		check_translation_result "$line"
		check_repair_result "$line"
		update_repair_scope_and_separate_files "$line"
		update_repair_count "$line"
		save_repair "$line" # must come after update_repair_scope_and_separate_files
		check_time_to_first_repair "$line" # must come after update_repair_count
		echo $line # so that AllRepair output remains the same
	done
}

initialize_settings_printing () {
	if [[ "$1" == "$SETTINGS_PREFIX"* ]]; then
		echo "$REPAIR_INIT_STRING" >> "$repairs_filename"
	fi
}

initialize_repair_scope () {
	if [[ "$1" == "Repairing file "* ]]; then
		in_repair_scope=0
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
		for setting_key in "${setting_keys[@]}"; do 
			if [[ "$setting_key" == "$3" ]]; then
				echo "$1" >> "$repairs_filename"
			fi
		done
	fi
}

calculate_total_time_to_first_Repair () {
	if [[ ! -z "${current_row["timetofirst"]}" ]]; then
		current_row["totaltofirst"]=`echo "${current_row["translationtime"]:-0} + ${current_row["timetofirst"]}" | bc`
	fi
}

check_translation_result () {
	if [[ $1 == "AllRepair: TRANSLATION PROCESS TERMINATED SUCCESSFULLY" ]]; then
		current_row["translation"]="SUCCESS"
	elif [[ $1 == "AllRepair: ERROR DURING TRANSLATION" ]]; then
		current_row["translation"]="FAILURE"
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

update_repair_scope_and_separate_files () {
	if [[ "$1" == "-------------"* ]]; then
		# if first repair- print line to separate this file for previous files
		if [ ${current_row["numrepairs"]} -eq 0 ]; then
			echo "$REPAIR_INIT_STRING" >> "$repairs_filename"
		fi 
		in_repair_scope=$((1-in_repair_scope))
	fi
}

update_repair_count () {
	if [[ $1 == "Possible repair:" ]]; then
		let current_row["numrepairs"]+=1
	fi
}

save_repair () {
	if ((in_repair_scope)); then
		echo "$1" >> "$repairs_filename"
	fi
}

check_time_to_first_repair () {
	if [ ${current_row["numrepairs"]} -eq 1 ]; then
		check_prefix_string_and_save "$1" "Elapsed time: " "timetofirst"
	fi
}

main "$@"
