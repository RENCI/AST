##############
# Docker file for the creation of the adcirc support tools (AST).
##############
FROM continuumio/miniconda3

# get some credit
LABEL maintainer="jtilson@renci.org"

# make sure the container is up-to-date
RUN apt-get update

# Start off getting Python 3.7.3
RUN conda install  -y python=3.7.3

# update conda and set the download channel
RUN conda update conda && \
    conda config --add channels conda-forge

# tell conda what the shell is
RUN conda init bash

# create the non-root user
RUN useradd -m -d /home/nru -u 1000 nru

# make sure everything is read/write
RUN chmod 777 -R /home/nru

# make d directory for the repos and go there
RUN mkdir /home/nru/repo
WORKDIR /home/nru/repo

# get the repos - needs to be made public first
RUN git clone https://github.com/RENCI/AST.git
               
# move to the deploy directory
WORKDIR /home/nru/repo/AST/deploy
                                
# install the pip requirements
RUN pip install -r pip_requirements.txt

# make a temporary directory for the output.
# this should eventually point a common PV
RUN mkdir /home/nru/repo/AST/pipelines/temp

# make sure everything is read/write
RUN chmod 777 -R /home/nru

# switch to the non-root user
USER nru

# change to the noaa directory
WORKDIR /home/nru/repo/noaa_coops

# run the noaa seteup
RUN python setup.py install --user
                        
# change to the pipelines directory                        
WORKDIR /home/nru/repo/AST/pipelines

# set the python path
ENV PYTHONPATH=/home/nru/repo/AST

# set the location of the output directory
#ENV RUNTIMEDIR=/data

##########
# The container is ready to accept the launch commands.
# generally from the harvester or processing subdirectories
##########
