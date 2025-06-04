#!/bin/bash
DIRECTORIES=../students/*
for d in $DIRECTORIES
do
    echo "$d/A3/output.py"  

    more "$d/A3/backtracking.py" > "$d/A3/output.py"; 
	tail -n+5 "$d/A3//csp_problems.py" >> "$d/A3/output.py"; 
	tail -n+3 "$d/A3/constraints.py" >> "$d/A3/output.py"; 
    
done
