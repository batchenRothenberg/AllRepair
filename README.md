# AllRepair

AllRepair is a mutation-based repair tool for C programs equipped with assertions in the code.

More details on the repair method behind AllRepair can be found in our paper
"Sound and Complete Mutation-Based Program Repair":

https://link.springer.com/chapter/10.1007%2F978-3-319-48989-6_36

##########################################################################################

### Installation:

*Note: If you want to avoid the installation pain you can download a VM with AllRepair already installed from our website:
TODO: Add url *

TODO: Add instructions....

##########################################################################################

### Usage:

To run AllRepair, go to directory scripts and run the AllRepair.sh script using the following command:

./AllRepair.sh [FileName] [Options]

For example, running 

./AllRepair.sh Examples/ex1.c -m 1 -b 5 -s 1

Will return all ways to reapir program ex1.c (from folder Examples) 
