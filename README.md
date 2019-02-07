# AllRepair

AllRepair is a mutation-based repair tool for C programs equipped with assertions in the code.

More details on the repair method behind AllRepair can be found in our paper
"Sound and Complete Mutation-Based Program Repair":

https://link.springer.com/chapter/10.1007%2F978-3-319-48989-6_36

##########################################################################################

### Building instructions (currently available only for Linux Debian-like distrubutions):

1. Install all pre-requists using:

          sudo apt-get install g++ gcc flex bison make git libwww-perl patch libz-dev python-z3

2. Download AllRepair source code using:

          git clone https://github.com/batchenRothenberg/AllRepair.git

3. Obtain InGeneer submodule:
          
          cd AllRepair
          git submodule init python/InGeneer
          git submodule update --remote python/InGeneer
          
4. Build the translation and mutation units (altered CBMC) by running "make" in the AllRepair/src directory.

5. Build the repair unit (altered MARCO), by running "make" in the AllRepair/python/pyminisolvers directory.

##########################################################################################

### Usage:

To run AllRepair, go to directory scripts and run the AllRepair.sh script using the following command:

                              ./AllRepair.sh [FileNames] [Options]

For example, running 

                              ./AllRepair.sh Examples/ex1.c -m 1 -b 5 -s 1

Will return all ways to reapir program ex1.c (from folder Examples) using mutation level 1, with the unwinding bound set to 5 and the maximum repair size is 1 (only one mutation at a time).

To see the complete list of options and their meaning, run:

                              ./AllRepair.sh -h
                              
Running AllRepair with a direcory name as FileName will result in the individual repair of all .c files in that directory.

##########################################################################################

### Interpretting the output:

Output lines beginning with "AllRepair: " and in capital letters are output lines displayed by the AllRepair script itself.
These lines should give you an idea of what is going on (translation/repair) and if it is going on succesfully.
Other lines are redirected output from the translation and the repair units, including more details.

Once AllRepair finds a possible repair it displays it like this:

          \------------------
          Possible Repair: ...
          In file... 
          Replace ..
          with
          ...
          In file... 
          Replace ..
          with
          ...
          \------------------
          
Which represents the patch you need to apply to the original program in order to repair it.
Note that since mutations are applied for a simplified version of the program, patch instructions sometimes require some translation.
For example, if your program contains the instruction i++, a repair might tell you to replace i=i+1 with i=i-1, which corresponds to replacing i++ with i--.

The final line of the output should always contain the result of the repair process, from within the following options:
SEARCH SPACE WAS COVERED SUCCESFULLY - all mutated programs in the search space were examined;
FAILURE - an exception or an out-of-memory error has occured;
TIMEOUT - timeout was reached (-t flag);
REPAIR LIMIT REACHED - tool has found the requiested number of repairs (-r flag);
PROGRAMS LIMIT REACHED - tool has inspected the requested number of programs (-p flag);
SIZE LIMIT REACHED - tool has succesfully covered the search space of mutated programs of at most the requested size (-s flag);
INTERUPTED  - tool was interrupted (e.g., by pressing ctrl+C);
ORIGINAL PROGRAM IS CORRECT - the program supplied did not contain a bug, or the bug was undetectable using the given specification and unwinding bound.

*Note that AllRepair will not stop once a repair is found, unless you'll tell it to, using the -r flag. So, the expected result in most cases should be to reach some limit (timeout/repair limit/size limit/program limit)*.



