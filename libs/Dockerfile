FROM ubuntu:focal

COPY . /pyfalcon
RUN apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install python3.9 build-essential curl g++ gfortran gettext zlib1g-dev openmpi-bin libhdf5-serial-dev python-is-python3 python3-pip git python3-dev
RUN pip3 install numpy matplotlib pandas pyyaml amuse-framework argparse astropy
RUN make -C pyfalcon/pyfalcon pyfalcon
CMD echo "Done"
