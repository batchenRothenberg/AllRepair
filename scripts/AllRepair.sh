# Script template taken from: https://gist.github.com/shakefu/2765260#file-example-sh
#set -e #exit on first error - not needed because of error handaling in script
#set -x #for debug: echo commands before execution

#set PYTHONPATH to z3 location
OLDPYTHONPATH=$PYTHONPATH
export PYTHONPATH="$OLDPYTHONPATH:/usr/lib/python2.7/dist-packages/z3"

# Option defaults
UNWIND=5
MUTATION=1
TRANSLATE=1
REPAIR=1
KEEP=0
TRANSLATIONOUT=0
REPAIROUT=0
BLOCK="basic"

# init list of code file and directory names 
FILES=""
DIRS=""

# getopts string
# This string needs to be updated with the single character options (e.g. -f)
opts="ufmntsphr:"

# always clean before exit
clean(){
	# delete files created by script
	if [[ -f $creating_file ]] && [[ $KEEP -ne 1 ]] && [[ $REPAIR -ne 0 ]]; then
		#echo "Last file created: $creating_file";
		rm $creating_file
	fi
	# restore PYTHONPATH
	export PYTHONPATH=$OLDPYTHONPATH
}
trap clean exit

# Gets the command name without path
cmd(){ echo `basename $0`; }

# Help command output
usage(){
echo "\
`cmd` [FileName...] [Option...]
-h, --help; Display this manual.
-u num, --unwind num; Set the unwinding bound to num (loops an function calls will be inlined num times). Default: 5.
-f func, --function func; Consider func as the entry point of the program (sets initial arguments of func non-deterministicly).
-m num, --mutation num; Set mutation level to num (num must be either 1 or 2). Default: 1.
-n func_list, --no-mut func_list; Do not mutate any code from functions in func_list. Argument func_list should be a list of function names, separated by commas. 
-t k, --timeout k; Sets a timeout of k seconds.
-s k, --size-limit k; Limits the repair size to k (only programs with at most k mutations at once will be inspected).
-p k, --program-limit k; Limits the number of inspected programs to k.
-r k, --repair-limit k; Stop after k possible repairs are found.
--only-translate; Stop after translation phase, wihtout doing repair. When this option is set, the result is a <file>.gsmt2 file for each <file>.c in the input.
--only-repair; Start from repair, without translating first. When this option is set, a file named <file>.gsmt2 is expected to exist for every <file>.c in the input.
--keep-translation; Do not earse the intermediate gsmt2 files generated by the translation unit.
--translation-out; Save the output of the translation phase to a file (seperately for each input file).
--repair-out; Save the output of the repair phase to a file (seperately for each input file).
--block-incorrect method; Use 'method' to block programs that were found to be incorrect. 'method' should be either 'basic' (block the found program alone), 'slicing' (block all programs with the same dynamic slice as in the found program) or 'generaliztion' (block all programs found using the error-generalization algorithm). Default: basic.  
" | column -t -s ";"
}

# Invalid option error message
error(){
    echo "`cmd`: invalid option -- '$1'";
    echo "Try '`cmd` -h' for more information.";
    exit 1;
}

# File not found error message
file_error(){
    echo "File '$1' not found";
    exit 1;
}

# function to run CBMC
cbmc(){
	out_name=`echo $1 | tr "/" "_"`
	out_name_no_extension="${out_name%.*}"

	echo "AllRepair: TRANSLATING ..."
	creating_file="$out_name_no_extension.gsmt2"
	if [[ $TRANSLATIONOUT -eq 1 ]]; then
		if [[ ! -d translation_out ]]; then
			mkdir translation_out
		fi
		../src/cbmc/cbmc $1 ${FUNCTION+"--function"} $FUNCTION ${UNWIND+"--unwind"} $UNWIND ${MUTATION+"--mutations"} $MUTATION ${NOMUT+"--no-mut"} $NOMUT --z3 --no-unwinding-assertions --no-propagation --error-label ERROR --bounds-check --pointer-check --outfile $out_name_no_extension.gsmt2 &> translation_out/$out_name_no_extension.tout
	else
		../src/cbmc/cbmc $1 ${FUNCTION+"--function"} $FUNCTION ${UNWIND+"--unwind"} $UNWIND ${MUTATION+"--mutations"} $MUTATION ${NOMUT+"--no-mut"} $NOMUT --z3 --no-unwinding-assertions --no-propagation --error-label ERROR --bounds-check --pointer-check --outfile $out_name_no_extension.gsmt2	
	fi
	return $?
}

# function to run MARCO
marco(){
	#echo "I am running MARCO on $1"
	out_name=`echo $1 | tr "/" "_"`
	out_name_no_extension="${out_name%.*}"

	echo "AllRepair: SEARCHING FOR REPAIR ..."
	if [[ $REPAIROUT -eq 1 ]]; then
		if [[ ! -d repair_out ]]; then
			mkdir repair_out
		fi
		../python/batmarco.py ${out_name_no_extension}.gsmt2 ${TIMEOUT+"-T"} $TIMEOUT ${REPAIRLIMIT+"-n"} $REPAIRLIMIT ${SIZELIMIT+"-k"} $SIZELIMIT ${PROGRAMLIMIT+"-l"} $PROGRAMLIMIT ${BLOCK+"--blockrepair"} $BLOCK --smt -v -s -a --smus &> repair_out/${out_name_no_extension}.rout
	else
		../python/batmarco.py ${out_name_no_extension}.gsmt2 ${TIMEOUT+"-T"} $TIMEOUT ${REPAIRLIMIT+"-n"} $REPAIRLIMIT ${SIZELIMIT+"-k"} $SIZELIMIT ${PROGRAMLIMIT+"-l"} $PROGRAMLIMIT ${BLOCK+"--blockrepair"} $BLOCK --smt -v -s -a --smus
	fi
}


# There's two passes here. The first pass handles the long options and
# any short option that is already in canonical form. The second pass
# uses `getopt` to canonicalize any remaining short options and handle
# them
for pass in 1 2; do
    while [ -n "$1" ]; do
        case $1 in
            --) shift; break;;
            -*) case $1 in
					-h|--help)     		usage; exit 0;;
					-u|--unwind)     	UNWIND=$2; shift;;
            		-f|--function)   	FUNCTION=$2; shift;;
            		-m|--mutation)   	MUTATION=$2; shift;;
        			-n|--no-mut)        NOMUT=$2; shift;;
            		-t|--timeout)      	TIMEOUT=$2; shift;;
            		-s|--size-limit)    SIZELIMIT=$2; shift;;
            		-p|--program-limit) PROGRAMLIMIT=$2; shift;;
            		-r|--repair-limit) 	REPAIRLIMIT=$2; shift;;
					--only-translate)	REPAIR=0;;
					--only-repair)		TRANSLATE=0;;
					--keep-translation) KEEP=1;;
					--translation-out)	TRANSLATIONOUT=1;;
					--repair-out)		REPAIROUT=1;;
					--block-incorrect)		BLOCK=$2; shift;;
            		--*)	error $1;;
       				-*)	if [ $pass -eq 1 ]; then ARGS="$ARGS $1";
                               else error $1; fi;;
        		esac;;
	    	*.c) if [[ -f $1 ]]; then FILES="${FILES}"$'\n'"${1}"; else file_error $1; fi;;
            *)  if [[ -d $1 ]]; then DIRS="$DIRS $1"; 
				else
                  if [[ $pass -eq 1 ]]; then ARGS="$ARGS $1";
                  else error $1; fi;
				fi;;
		esac
        shift
    done
    if [[ $pass -eq 1 ]]; then ARGS=`getopt $opts $ARGS`
        if [[ $? != 0 ]]; then echo "Try '`cmd` -h' for more information."; exit 2; fi; set -- $ARGS
    fi
done

# echo "UNWIND=$UNWIND FUNCTION=$FUNCTION MUTATION=$MUTATION NOMUT=$NOMUT TIME=$TIMEOUT SIZE=$SIZELIMIT REPAIRLIM=$REPAIRLIMIT PROG=$PROGRAMLIMIT BLOCK=$BLOCK"
# echo "FILES=$FILES"
# echo "DIRS=$DIRS"

#check parameter integrity
if [[ $FILES == "" ]] && [[ $DIRS == "" ]]; then
	echo "You must specify at least one input file (<file>.c) or directory"
	exit 1
fi
if [ $BLOCK != "basic" ] && [ $BLOCK != "slicing" ] && [ $BLOCK != "generalization" ]; then
	echo "Wrong method for --block-incorrect ($BLOCK). Method can be either basic, slicing or generalization."
	exit 1
fi
if [ $BLOCK == "" ]; then
	echo "Argument --block-incorrect should be followed by one of the following methods: basic, slicing or generalization."
	exit 1
fi


# Handle positional arguments
if [ -n "$*" ]; then
    echo "`cmd`: Extra arguments -- $*"
	echo "Arguments should be either a C file, a directory or a valid option."
    echo "Try '`cmd` -h' for more information."
    exit 1
fi

# Set verbosity
#if [ "0$VERBOSE" -eq 0 ]; then
    # Default, quiet
#    :
#fi
#if [ $VERBOSE -eq 1 ]; then
    # Enable log messages
#    :
#fi
#if [ $VERBOSE -ge 2 ]; then
    # Enable high verbosity
#    :
#fi
#if [ $VERBOSE -ge 3 ]; then
    # Enable debug verbosity
#    :
#fi

# get individual filenames from FILES and DIRS
if [[ "$DIRS" ]]; then
	DIRFILES=`find $DIRS -name '*.c'` #find all c files in directories (including sub-directories)
	ALLFILES="$FILES
$DIRFILES" #add command-line files
else
	ALLFILES="$FILES"
fi

OIFS="$IFS" #variable content is split according to characters from IFS
IFS=$'\n' #split only on new line and not space or tab (allows filenames with spaces)

#Procces files
for file in $ALLFILES ; do
	echo ""
	echo "		Repairing file $file"
	echo ""
	if [[ $TRANSLATE -eq 1 ]]; then
		cbmc $file
		cbmc_res=$?
		if [[ $cbmc_res -ne 10 ]]; then
			echo "AllRepair: ERROR: translation error"
		fi	
	fi
	if [[ $REPAIR -eq 1 ]] && ([[ $cbmc_res -eq 10 ]] || [[ $TRANSLATE -ne 1 ]]); then
		marco $file
	fi
	out_name=`echo $file | tr "/" "_"`
	out_name_no_extension="${out_name%.*}"
	if  [[ $KEEP -ne 1 ]] && [[ $REPAIR -eq 1 ]] && [[ $TRANSLATE -eq 1 ]] && [[ -f ${out_name_no_extension}.gsmt2 ]]; then
		rm ${out_name_no_extension}.gsmt2
	fi
	echo " ____________________________________________________________________________________"
done
IFS="$OIFS" #go back to normal splitting
