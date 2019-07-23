
# dockerfile
#Run it using docker run -ti -e DISPLAY=ip_address:0.0 docker_image_name
#In Windows installing VcXsrv Windows X Server is needed for sumo-gui to work.
# Use ubuntu as a parent image - 18.04 has LTS
FROM ubuntu:18.04

# MAINTAINER Jakob Smretschnig <jakob.smretschnig@tum.de>, based on docker-image by Bo Gao <bogao@dcs.warwick.ac.uk>
LABEL Description="Dockerised SUMO (Simulation of Urban MObility)"

ENV SUMO_HOME /sumo

# Install system dependencies
RUN apt-get -qq update && apt-get -qq install \
    cmake python g++ libxerces-c-dev libfox-1.6-dev libgdal-dev libproj-dev libgl2ps-dev swig git \
    ffmpeg python-dev \
    wget \
    python2.7 \
    sudo \
    xorg \
    python-pip \
    python-rtree

# Download and build sumo
RUN git clone --recursive https://github.com/eclipse/sumo --verbose --progress
RUN mkdir sumo/build/cmake-build
WORKDIR sumo/build/cmake-build
RUN cmake ../..
RUN make -j8

# Install python dependencies
COPY . /
COPY data /
RUN pip install -r /execution/requirements.txt


# TODO
#RUN apt-get -qq update && apt-get -qq install python-tk python3-tk
#RUN cd $SUMO_HOME && ./configure && make install
WORKDIR /
EXPOSE 4040

ENTRYPOINT ["python", "execution/startSimulation.py"]
