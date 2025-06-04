#!/bin/bash
#script to move files into subdirectories
DIRECTORIES=students/*
for d in $DIRECTORIES
do
    echo "$d/agent.py"  
    mkdir "$d/A3"    
    mv "$d/agent.py" "$d/A3/agent.py"       
done
