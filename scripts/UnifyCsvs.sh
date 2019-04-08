#!/bin/bash

declare -a column_keys=( "filename" "category" "hard" "soft" "programs" "translation" "repair" "numrepairs" "totaltofirst" "translationtime" "timetofirst" "maxinspected"  "satchecktotal" "satblocktotal" "smttotal" "setuptotal" "total" "smtcount" "smtper" "mutlevel" "bound" "timeout" "replimit" "sizelimit" "proglimit" "incremental" )
declare -A column_titles=( ["filename"]="file name" ["category"]="category" ["hard"]="hard constraints" ["soft"]="max mutation size" ["programs"]="mutated programs" ["translation"]="translation result" ["repair"]="repair result" ["numrepairs"]="found repairs" ["timetofirst"]="time to first repair [s]" ["maxinspected"]="max inspected size" ["satchecktotal"]="sat check [s]" ["satblocktotal"]="sat block [s]" ["smttotal"]="smt check [s]" ["setuptotal"]="setup [s]" ["smtcount"]="smt check count" ["total"]="total repair time [s]" ["translationtime"]="translation time [s]" ["totaltofirst"]="total time to first repair" ["smtper"]="SMT check per" ["mutlevel"]="mutation level" ["bound"]="unwinding bound" ["timeout"]="timeout" ["replimit"]="repair limit" ["sizelimit"]="size limit" ["proglimit"]="program limit" ["incremental"]="SMT incremental method" )

main() {
	get_input_filenames $1
	get_output_file $2
	print_title
	for file in $filenames; do
		cat $file | evaluate_file
	done
}

print_title () {
	echo -n "" > $output_file # rewrite file
	for key in "${column_keys[@]}"; do 
		echo -n "${column_titles[$key]}," >> $output_file
	done
	echo "" >> $output_file
}

get_output_file () {
	if ! [ -z "$1" ]; then
		output_file=$1
	else	
		output_file="AllRepair_joined_csv_`date +'%d_%m_%Y_%H_%M_%S'`.csv"
	fi
}

get_input_filenames () {
	if [[ -d $1 ]]; then
		filenames=`find $1 -name '*.csv'` #find all csv files in directories (including sub-directories)
	else
		echo "$1 is not a directory"
		exit
	fi
}

evaluate_file () {
	read date_string
	read settings_string
	parse_settings "$settings_string"
	echo "mutation=$mutation_level unwind=$unwinding_bound timeout=$timeout replim=$repair_limit sizlim=$size_limit proglim=$program_limit incremental=$incremental" 
	read title_string
	while read line; do
		echo "$line" | parse_category_and_print
		echo "$mutation_level,$unwinding_bound,$timeout,$repair_limit,$size_limit,$program_limit,$incremental" >> $output_file
	done
}

parse_category_and_print () {
	OIFS=$IFS 
	IFS=, # split only on commas
	read first rest
	filename_only=`basename $first`
	category=${filename_only%_v*}
	echo -n "$first,$category,$rest" >> $output_file
	IFS=$OIFS
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
	if echo "$1" | grep -q ".*SMT incremental method=.*"; then
		incremental=`echo "$1" | sed 's/.*SMT incremental method=\([a-z]*\).*/\1/'`
	fi
}

main "$@"

