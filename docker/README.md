# README for AllRepair Docker

# Build AllRepair using Docker
From the cd where AllRepair is located run (note the period at the end):

$ docker build -t allrepair-build -f docker/allrepair.Dockerfile .

The above will copy your local AllRepair code (with changes, if any) to a conainer and build the code.
To run AllRepair inside the container run:

$ docker run -v `pwd`:/host -it allrepair-build

The container will start from within the scripts directory, from which you can simply run the AllRepair script as you please, e.g.:

$ ./AllRepair.sh Benchmarks/Tcas/tcas_v1.c

To access files on the host machine (outside the container) use the '/host' prefix, which points to the directory from which you run the 'docker run' command.
For example, if the host directory contains a file named bug.c, the following command will run AllRepair on the file and save the output to bug.out (created on the host directory as well):

$ ./AllRepair.sh /host/bug.c > /host/bug.out
