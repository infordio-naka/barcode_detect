#! /bin/bash

# python gen_barcode/gen_barcode.py
opencv_createsamples -info positive.dat -vec positive.vec -num 7000 -w 40 -h 40
opencv_traincascade -data cascade/ -vec positive.vec -bg negative.dat -numPos 7000 -numNeg 5000 -w 40 -h 40
