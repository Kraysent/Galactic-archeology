FROM ubuntu:22.04
RUN apt-get update && apt-get install build-essential gfortran python3-dev \
    libopenmpi-dev openmpi-bin \
    libgsl-dev cmake libfftw3-3 libfftw3-dev \
    libgmp3-dev libmpfr6 libmpfr-dev \
    libhdf5-serial-dev hdf5-tools \
    libblas-dev liblapack-dev git python3-pip -y
COPY requirements.txt /requirements.txt
RUN python3 -m pip install -r requirements.txt
RUN git clone https://github.com/GalacticDynamics-Oxford/pyfalcon.git
RUN cd pyfalcon && python3 setup.py install

CMD ["python3 -c 'print(\"Hello world\")'"]
