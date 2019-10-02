#!/bin/bash

base_dir="AllRepairResults"
separating_string="___________________"
declare -a column_keys=( "filename" "hard" "soft" "programs" "translation" "repair" "numrepairs" "totaltofirst" "translationtime" "timetofirst" "maxinspected"  "satchecktotal" "satblocktotal" "smttotal" "setuptotal" "readgsmt2total" "total" "smtcount" "smtper" "mutlevel" "bound" "timeout" "replimit" "sizelimit" "proglimit" "incremental" "block" "safety" )
declare -A column_titles=( ["filename"]="file name" ["hard"]="hard constraints" ["soft"]="max mutation size" ["programs"]="mutated programs" ["translation"]="translation result" ["repair"]="repair result" ["numrepairs"]="found repairs" ["timetofirst"]="time to first repair [s]" ["maxinspected"]="max inspected size" ["satchecktotal"]="sat check [s]" ["satblocktotal"]="sat block [s]" ["smttotal"]="smt check [s]" ["setuptotal"]="setup [s]" ["readgsmt2total"]="parse gsmt2 [s]" ["smtcount"]="smt check count" ["total"]="total repair time [s]" ["translationtime"]="translation time [s]" ["totaltofirst"]="total time to first repair" ["smtper"]="SMT check per" ["mutlevel"]="mutation level" ["bound"]="unwinding bound" ["timeout"]="timeout" ["replimit"]="#repairs limit" ["sizelimit"]="mutation size limit" ["proglimit"]="#progs limit" ["incremental"]="SMT incremental method" ["block"]="blocking method" ["safety"]="safety checks enabled?" )
declare -A prefix_strings=( ["filename"]="Repairing file " ["hard"]="Hard constraints (group 0): " ["soft"]="Max mutation size: " ["programs"]="Mutated programs in search space: " ["maxinspected"]="Max inspected size: " ["satchecktotal"]="SAT check : " ["satblocktotal"]="SAT block : " ["smttotal"]="SMT check : " ["setuptotal"]="Setup : " ["readgsmt2total"]="Parse gsmt2 : " ["total"]="total : " ["smtcount"]="SMT check count :" ["translationtime"]="AllRepair: Translation duration: " ["smtper"]="SMT check per :" )
declare -A current_row
in_repair_scope=0 # boolean

# Option defaults
UNWIND=5
MUTATION=1
TRANSLATE=1
REPAIR=1
KEEP=0
TRANSLATIONOUT=0
REPAIROUT=0
BLOCK="basic"
INCREMENTAL="none"

# init arrays
DIRS=()
CONSTANT_ALLREPAIR_ARGS=()
CHANGING_ALLREPAIR_ARGS=()
MUTATION_LEVELS=()
UNWINDING_BOUNDS=()
BLOCKING_METHODS=()
INCREMENTAL_METHODS=()
TIMEOUT_ARRAY=()
SIZELIMIT_ARRAY=()
PROGLIMIT_ARRAY=()
REPAIRLIMIT_ARRAY=()

# getopts string
# This string needs to be updated with the single character options (e.g. -f)
opts="ufmntsphr:"

main() {
	parse_options "$@" # save argument values into local variables
	check_input_dir_integrity # exit if there is less/more than one input directory
	# print_options
	parse_multiple_choise_options # e.g., MUTATION="1,2" to MUTATION_LEVELS=(1,2)
	check_integrity_of_multiple_choice # e.g., that each mutation level is either 1 or 2
	get_constant_allrepair_args # save arguments that remain the same across all files. e.g., --no-mut
	create_output_directory
	determine_csv_filename
	determine_repair_table_filename
	input_dir="${DIRS[0]}"
	for file in "$input_dir"/* ; do
	#file can be either a file or a dir(in which case all *.c files under it will be repaired together)
		determine_repairs_filename "$file"
		SETTINGS_ARRAY=(MUTATION_LEVELS UNWINDING_BOUNDS BLOCKING_METHODS INCREMENTAL_METHODS TIMEOUT_ARRAY SIZELIMIT_ARRAY PROGLIMIT_ARRAY REPAIRLIMIT_ARRAY)
		recursive_run_allrepair "$file" 0
	done
}

recursive_run_allrepair () { # parameters: file (file to run AllRepair on), settings_index (current index in SETTINGS_ARRAY)
	if (( $2 == ${#SETTINGS_ARRAY[@]} )); then
		echo "./AllRepair.sh" "$1" "${CONSTANT_ALLREPAIR_ARGS[@]}" "--group-files" "${CHANGING_ALLREPAIR_ARGS[@]}" "2>&1 | ./ParseAllRepair.sh" "$CSV_FILENAME" "$REPAIR_FILENAME" "$REPAIR_TABLE_FILENAME"
		./AllRepair.sh "$1" "${CONSTANT_ALLREPAIR_ARGS[@]}" "--group-files" "${CHANGING_ALLREPAIR_ARGS[@]}" 2>&1 | ./ParseAllRepair.sh "$CSV_FILENAME" "$REPAIR_FILENAME" "$REPAIR_TABLE_FILENAME"
		# ./AllRepair.sh "$1" "${CONSTANT_ALLREPAIR_ARGS[@]}" "--group-files" "${CHANGING_ALLREPAIR_ARGS[@]}"
		return 0
	fi
	array_name="${SETTINGS_ARRAY[$2]}"
	eval array_length="\${#${array_name}[@]}"
	eval array_content=("\${${array_name}[@]}")
	# for debug
	# echo "NAME: $array_name, LEN: $array_length, CONTENT: ${array_content[@]}"
	let index=$2+1
	if (( $array_length == 0 )); then
		recursive_run_allrepair "$1" "$index"
	else
		for element in ${array_content[@]}; do
			get_option_string_from_array_name "$array_name"
			CHANGING_ALLREPAIR_ARGS+=("$CURR_OPTION")
			CHANGING_ALLREPAIR_ARGS+=("$element")
			recursive_run_allrepair "$1" "$index"
			# re-set variables that were changed during recursion and are used again in the loop
			array_name="${SETTINGS_ARRAY[$2]}" 
			let index=$2+1
			# unset changes to CHANGING_ALLREPAIR_ARGS
			unset 'CHANGING_ALLREPAIR_ARGS[${#CHANGING_ALLREPAIR_ARGS[@]}-1]'
			unset 'CHANGING_ALLREPAIR_ARGS[${#CHANGING_ALLREPAIR_ARGS[@]}-1]'
		done
	fi
}

get_option_string_from_array_name () {
	if [[ "$1" == "MUTATION_LEVELS" ]]; then
		CURR_OPTION="-m"
	fi
	if [[ "$1" == "UNWINDING_BOUNDS" ]]; then
		CURR_OPTION="-u"
	fi
	if [[ "$1" == "BLOCKING_METHODS" ]]; then
		CURR_OPTION="--block-incorrect"
	fi
	if [[ "$1" == "INCREMENTAL_METHODS" ]]; then
		CURR_OPTION="--incremental"
	fi
	if [[ "$1" == "TIMEOUT_ARRAY" ]]; then
		CURR_OPTION="-t"
	fi
	if [[ "$1" == "SIZELIMIT_ARRAY" ]]; then
		CURR_OPTION="-s"
	fi
	if [[ "$1" == "PROGLIMIT_ARRAY" ]]; then
		CURR_OPTION="-p"
	fi
	if [[ "$1" == "REPAIRLIMIT_ARRAY" ]]; then
		CURR_OPTION="-r"
	fi
}

parse_options () {
# There's two passes here. The first pass handles the long options and
# any short option that is already in canonical form. The second pass
# uses `getopt` to canonicalize any remaining short options and handle
# them
for pass in 1 2; do
    while [ -n "$1" ]; do
        case $1 in
            --) ;;
            -*) case $1 in
			-u|--unwind)     	UNWIND=$2; shift;;
            		-f|--function)   	FUNCTION=$2; shift;;
            		-m|--mutation)   	MUTATION=$2; shift;;
        		-n|--no-mut)        	NOMUT=$2; shift;;
            		-t|--timeout)      	TIMEOUT=$2; shift;;
            		-s|--size-limit)    	SIZELIMIT=$2; shift;;
            		-p|--program-limit) 	PROGRAMLIMIT=$2; shift;;
            		-r|--repair-limit) 	REPAIRLIMIT=$2; shift;;
			--only-translate)	REPAIR=0;;
			--only-repair)		TRANSLATE=0;;
			--keep-translation) 	KEEP=1;;
			--translation-out)	TRANSLATIONOUT=1;;
			--repair-out)		REPAIROUT=1;;
			--block-incorrect)	BLOCK=$2; shift;;
			--incremental)		INCREMENTAL=$2; shift;;
			--error-label)		ERRORLABEL=$2; shift;;
			--builtin-checks)	BUILTIN=1;;
			--no-built-in-assertions)	NOBUILTINASSERTIONS="--no-built-in-assertions";;
			--no-assertions)		NOASSERTIONS="--no-assertions";;
			--no-assumptions)		NOASSUMPTIONS="--no-assumptions";;
			--name)			NAME=$2; shift;;
            		--*)	echo "Invalid option -- '$1'"; exit 1;;
       			-*)	if [ $pass -eq 1 ]; then ARGS="$ARGS $1";
                               else echo "Invalid option -- '$1'"; exit 1; fi;;
        		esac;;
            *)  if [[ -d $1 ]]; then 
			DIRS+=("$1");
		else
                	if [[ $pass -eq 1 ]]; then 
				ARGS="$ARGS $1"
                  	else 
				echo "Invalid option -- '$1'" 
				exit 1 
			fi
		fi;;
		esac
        shift
    done
    if [[ $pass -eq 1 ]]; then 
	ARGS=`getopt $opts $ARGS`
        if [[ $? != 0 ]]; then 
		exit 1; 
	fi; 
	set -- $ARGS # sets positional arguments to $ARGS
    fi
done
}

print_options () {
echo "UNWIND: $UNWIND"
echo "FUNCTION: $FUNCTION"
echo "MUTATION: $MUTATION"
echo "NOMUT: $NOMUT"
echo "TIMEOUT: $TIMEOUT"
echo "SIZELIMIT: $SIZELIMIT"
echo "PROGRAMLIMIT: $PROGRAMLIMIT"
echo "REPAIRLIMIT: $REPAIRLIMIT"
echo "REPAIR: $REPAIR"
echo "TRANSLATE: $TRANSLATE"
echo "KEEPTRANSLATION: $KEEP"
echo "TRANSLATIONOUT: $TRANSLATIONOUT"
echo "REPAIROUT: $REPAIROUT"
echo "BLOCK: $BLOCK"
echo "INCREMENTAL: $INCREMENTAL"
echo "ERRORLABEL: $ERRORLABEL"
echo "BUILTIN: $BUILTIN"
echo "NO BUILTIN ASSERTIONS: $NOBUILTINASSERTIONS"
echo "NO ASSERTIONS: $NOASSERTIONS"
echo "NO ASSUMPTIONS: $NOASSUMPTIONS"
echo "NAME: $NAME"
}

check_input_dir_integrity () {
if (( ${#DIRS[@]} != 1 )); then
	echo "You must specify exactly one input directory (under which there can be sub-directories and/or individual files)."
	echo "Directories specified: ${DIRS[@]}"
	exit 1
fi
}

check_blocking_method_integrity () {
if [[ "$1" != "basic" ]] && [[ "$1" != "slicing" ]] && [[ "$1" != "generalization" ]]; then
	echo "Wrong method for --block-incorrect ($1). Method can be either basic, slicing or generalization."
	exit 1
fi
}

check_incremental_method_integrity () {
if [[ "$1" != "none" ]] && [[ "$1" != "pushpop" ]] && [[ "$1" != "assumptions" ]]; then
	echo "Wrong method for --incremental ($1). Method can be either none, pushpop or assumptions."
	exit 1
fi
}

check_mutation_level_integrity () {
if (( $1 != 1 )) && (( $1 != 2 )); then
	echo "Invalid mutation level ($1). Mutation level can be either 1 or 2."
	exit 1
fi
}

check_unwinding_bound_integrity () {
	is_numeral "$1"
	if (( "$?" != 0 )); then
		echo "Invalid unwinding bound ($1). Unwinding bounds must be numeric."	
		exit 1
	fi
}

check_timeout_integrity () {
	is_numeral "$1"
	if (( "$?" != 0 )); then
		echo "Invalid timeout ($1). Timeout must be numeric."	
		exit 1
	fi
}

check_size_limit_integrity () {
	is_numeral "$1"
	if (( "$?" != 0 )); then
		echo "Invalid size limit ($1). Limits must be numeric."	
		exit 1
	fi
}

check_program_limit_integrity () {
	is_numeral "$1"
	if (( "$?" != 0 )); then
		echo "Invalid programs limit ($1). Limits must be numeric."	
		exit 1
	fi
}

check_repair_limit_integrity () {
	is_numeral "$1"
	if (( "$?" != 0 )); then
		echo "Invalid repairs limit ($1). Limits must be numeric."	
		exit 1
	fi
}

is_numeral () {
if  [[ ! "$1" = *([0-9]) ]]; then
	return 1
fi
}

parse_multiple_choise_options () {
IFS=',' read -r -a MUTATION_LEVELS <<< "$MUTATION"
IFS=',' read -r -a UNWINDING_BOUNDS <<< "$UNWIND"
IFS=',' read -r -a BLOCKING_METHODS <<< "$BLOCK"
IFS=',' read -r -a INCREMENTAL_METHODS <<< "$INCREMENTAL"
IFS=',' read -r -a TIMEOUT_ARRAY <<< "$TIMEOUT"
IFS=',' read -r -a SIZELIMIT_ARRAY <<< "$SIZELIMIT"
IFS=',' read -r -a PROGLIMIT_ARRAY <<< "$PROGRAMLIMIT"
IFS=',' read -r -a REPAIRLIMIT_ARRAY <<< "$REPAIRLIMIT"
# for debug
# print_multiple_choice
}

print_multiple_choice () {
echo "MUTATIONS: ${MUTATION_LEVELS[@]}"
echo "UNWINDING_BOUNDS: ${UNWINDING_BOUNDS[@]}"
echo "BLOCKING_METHODS: ${BLOCKING_METHODS[@]}"
echo "INCREMENTAL_METHODS: ${INCREMENTAL_METHODS[@]}"
echo "TIEMOUTS: ${TIMEOUT_ARRAY[@]}"
echo "SIZE LIMITS: ${SIZELIMIT_ARRAY[@]}"
echo "PROGRAM LIMITS: ${PROGLIMIT_ARRAY[@]}"
echo "REPAIR LIMITS: ${REPAIRLIMIT_ARRAY[@]}"
}

check_integrity_of_multiple_choice () {
for m in ${MUTATION_LEVELS[@]}; do
	check_mutation_level_integrity "$m"
done
for bound in ${UNWINDING_BOUNDS[@]}; do
	check_unwinding_bound_integrity "$bound"
done
for block in ${BLOCKING_METHODS[@]}; do
	check_blocking_method_integrity "$block"
done
for inc in ${INCREMENTAL_METHODS[@]}; do
	check_incremental_method_integrity "$inc"
done
for timeout in ${TIMEOUT_ARRAY[@]}; do
	check_timeout_integrity "$timeout"
done
for sizelimit in ${SIZELIMIT_ARRAY[@]}; do
	check_size_limit_integrity "$sizelimit"
done
for proglimit in ${PROGLIMIT_ARRAY[@]}; do
	check_program_limit_integrity "$proglimit"
done
for repairlimit in ${REPAIRLIMIT_ARRAY[@]}; do
	check_repair_limit_integrity "$repairlimit"
done
}

get_constant_allrepair_args () {
if [[ ! -z "$FUNCTION" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("--function")
	CONSTANT_ALLREPAIR_ARGS+=("$FUNCTION")
fi
if [[ ! -z "$NOMUT" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("--no-mut")
	CONSTANT_ALLREPAIR_ARGS+=("$NOMUT")
fi
if (( "$REPAIR" == 0 )); then
	CONSTANT_ALLREPAIR_ARGS+=("--only-translate")
fi
if (( "$TRANSLATE" == 0 )); then
	CONSTANT_ALLREPAIR_ARGS+=("--only-repair")
fi
if (( "$KEEP" != 0 )); then
	CONSTANT_ALLREPAIR_ARGS+=("--keep-translation")
fi
if (( "$TRANSLATIONOUT" != 0 )); then
	CONSTANT_ALLREPAIR_ARGS+=("--translation-out")
fi
if (( "$REPAIROUT" != 0 )); then
	CONSTANT_ALLREPAIR_ARGS+=("--repair-out")
fi
if [[ ! -z "$ERRORLABEL" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("--error-label")
	CONSTANT_ALLREPAIR_ARGS+=("$ERRORLABEL")
fi
if [[ ! -z "$NOBUILTINASSERTIONS" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("$NOBUILTINASSERTIONS")
fi
if [[ ! -z "$NOASSERTIONS" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("$NOASSERTIONS")
fi
if [[ ! -z "$NOASSUMPTIONS" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("$NOASSUMPTIONS")
fi
if [[ ! -z "$BUILTIN" ]]; then
	CONSTANT_ALLREPAIR_ARGS+=("--bounds-check")
	CONSTANT_ALLREPAIR_ARGS+=("--div-by-zero-check")
fi
# for debug
# echo "${CONSTANT_ALLREPAIR_ARGS[@]}"
}

create_output_directory () {
# dir name in format $NAME(if assigned)-date_and_time-"commit"-commit_hash
DATE_AND_TIME=`date +'%d_%m_%Y_%H_%M_%S'`
COMMIT=`git rev-parse --short HEAD`
if [[ ! -z "$NAME" ]]; then
	results_dir="$NAME-$DATE_AND_TIME-commit-$COMMIT"
else
	results_dir="$DATE_AND_TIME-commit-$COMMIT"
fi
# Create if does not exist
if ! [ -d "$base_dir/$results_dir" ]; then
	mkdir -p "$base_dir/$results_dir"
fi
}

determine_csv_filename () {
CSV_FILENAME="$base_dir/${results_dir}/${results_dir}_results.csv"
# for debug
# echo "$CSV_FILENAME"
}

determine_repair_table_filename () {
REPAIR_TABLE_FILENAME="$base_dir/${results_dir}/${results_dir}_repair_table.csv"
# for debug
# echo "$REPAIR_TABLE_FILENAME"
}

determine_repairs_filename () {
filename_no_dir=`basename "$1"`
filename_no_dir_no_extension="${filename_no_dir%.c}"
REPAIR_FILENAME="$base_dir/${results_dir}/${results_dir}_${filename_no_dir_no_extension}_repairs.txt"
# for debug
# echo "$REPAIR_FILENAME"
}

main "$@"

