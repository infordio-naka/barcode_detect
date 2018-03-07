#! /bin/bash

rm -fr images/*; python gen_barcode/gen_barcode.py
opencv_createsamples -info positive.dat -vec positive.vec -num 30000 -w 40 -h 20
rm -fr cascade/*; opencv_traincascade -data cascade -vec positive.vec -bg negative.dat -numStages 2 -numPos 25000 -numNeg 20000 -w 40 -h 20 -featureType LBP
