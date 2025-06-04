#!/bin/bash

#change DIRECTORIES to name of directory with student submissions
DIRECTORIES=Assignment1/*

for d in $DIRECTORIES
do
    #uncomment to make subdirectory for student submissions and move files
    #extract name of student
    pattern="Assignment1/([^/].+)"

    if [[ $d =~ $pattern ]]
    then
      name="${BASH_REMATCH[1]}"

      if [ -f "$d/search.txt" ]; then
        echo "$name, 1"
        #cp "$d/games.txt" "/Users/JaglalLab/Desktop/CSC384/Self-Assessments/assessments/games-$name.txt"
        grep -o -i . "$d/search.txt" | wc -l
      else
        echo "$name, 0"
      fi
      
    else echo "error processing files in $d"
    fi
done
