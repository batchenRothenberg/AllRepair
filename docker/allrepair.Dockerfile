
# Pull base image.
FROM ubuntu:18.04

# Install dependencies
RUN apt-get update && \
	apt-get install -y g++ gcc flex bison make git libwww-perl patch libz-dev python-z3 bsdmainutils

# Copy AllRepair
COPY . /AllRepair

# Build the translation unit
RUN cd AllRepair/src && \
	make

# Build the mutation unit
RUN cd AllRepair/python/pyminisolvers && \
	make

WORKDIR /AllRepair/scripts

