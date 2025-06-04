#!/bin/bash
DIRECTORIES=../students/*
for d in $DIRECTORIES
do
    echo "$d/bnetbase.py"  
    mkdir "$d/A4"    
    mv "$d/bnetbase.py" "$d/A4/bnetbase.py"       
done
