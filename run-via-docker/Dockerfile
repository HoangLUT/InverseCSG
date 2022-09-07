# ubuntu base image
FROM ubuntu:16.04

# update package lists and upgrade packages
RUN apt-get update -y
RUN apt-get upgrade -y

# dependencies listed in github readme
RUN apt-get install -y build-essential autoconf libtool flex bison mercurial zsh cmake wget
# install maven
RUN apt-get install -y maven

# dependencies required to build python 3.7.7
RUN apt install -y zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev
RUN apt-get update

# download and install python 3.7.7
WORKDIR /usr/src/app
RUN wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz
RUN tar xzf Python-3.7.7.tgz
WORKDIR /usr/src/app/Python-3.7.7
RUN ./configure && make && make install

# download and install miniconda
WORKDIR /usr/src/app
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.12.0-Linux-x86_64.sh
RUN bash Miniconda3-py37_4.12.0-Linux-x86_64.sh -b -p $HOME/miniconda

# install a few more dependencies required by the install.py script
RUN apt-get install -y sudo unzip openjdk-8-jdk libcgal-dev git
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:ubuntu-toolchain-r/test -y
RUN apt-get update -y
RUN apt-get install -y gcc-snapshot
RUN apt-get update -y
RUN apt-get install -y gcc-6 g++-6
# activate conda and install dependencies
RUN bash -c 'source $HOME/miniconda/bin/activate && conda create -n inv_csg_env python=3.7 -y && conda activate inv_csg_env && python3 -m pip install -U pip setuptools && python3 -m pip install --upgrade pip && python3 -m pip install numpy scipy matplotlib ipython jupyter pandas sympy nose && python3 -m pip install -U scikit-learn'

# COPY source files into image
COPY . .

RUN python3 install.py -d ./build
