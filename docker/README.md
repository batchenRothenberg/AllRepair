# README for AllRepair Docker

# Build AllRepair using Docker
From the cd where AllRepair is located, run:
$ docker build -t allrepair-build -f docker/allrepair.Dockerfile .
The above will copy your local AllRepair code (with changes, if any) to a conainer, and build the code.
To run AllRepair inside the container, run:
$ docker run -v `pwd`:/host -it allrepair-build
The container will start from within the scripts directory, from which you can simply run the AllRepair script as you please, e.g.:
$ ./AllRepair.sh Benchmarks/Tcas/tcas_v1.c
