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

                              ./AllRepair.sh [FileName] [Options]

For example, running 

                              ./AllRepair.sh Examples/ex1.c -m 1 -b 5 -s 1

Will return all ways to reapir program ex1.c (from folder Examples) using mutation level 1, with the unwinding bound set to 5 and the maximum repair size is 1 (only one mutation at a time).

To see the complete list of options and their meaning, run:

                              ./AllRepair.sh -h

##########################################################################################

### Running the TCAS benchmark:

To run AllRepair on the TCAS benchmark under the same conditions as in the FM16 paper (link above), go to directory scripts and run the RunTcas.sh script using the following command:

                              ./RunTcas.sh

This will run AllRepair on all 41 versions of the TCAS benchmark using the same parameters as we used in the paper (unwinding bound of 5 and at most 2 mutations at once).
The repair process will stop once the first repair suggestion is found.
The script will create a folder named "repair_out" under scripts, in which you can find a file with the repair results for each of the TCAS versions.
If a repair was found, it will be described under the "possible solution" title (with "Elapsed time" being the time it took to find that repair, excluding program translation time). 
To run with mutation level 2 instead of 1 edit the script and replace "-m 1" with "-m 2".
To see more repair suggestions per program, delete the "-r 1" option.
Other options can be modified similarily.

**Warning: if you run the script twice, output files will be overwritten**

