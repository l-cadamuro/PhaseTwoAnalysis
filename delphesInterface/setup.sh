#!/bin/bash
PPOLDDIR=`pwd`
DELPHES_TAG=3.4.2pre13

echo $PPOLDDIR
wget https://github.com/delphes/delphes/archive/${DELPHES_TAG}.tar.gz
tar xfz ${DELPHES_TAG}.tar.gz
mv delphes-* delphes
cd delphes
pwd
source DelphesEnv.sh
./configure
sed -i -e 's/c++0x/c++1y/g' Makefile
make -j4  
cd $PPOLDDIR
source env.sh

cd $DANALYSISPATH
pwd
make -j3
cd $PPOLDDIR/ntupler
pwd
make -j3
cd -