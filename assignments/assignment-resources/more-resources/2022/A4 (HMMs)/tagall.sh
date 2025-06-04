#!/bin/bash

#change outfile to name of file you want to write to (to hold results)
outfile="/Users/JaglalLab/Desktop/CSC384/csc384-a3/grades.txt"

#change DIRECTORIES to name of directory with student submissions
DIRECTORIES=students/*
echo "utorid, prior_a, prior_b, transition_a, transition_b, emission_a, emission_b, tagging_small, tagging_large" > "$outfile"
for d in $DIRECTORIES
do
    #uncomment to make subdirectory for student submissions and move files
    #mkdir "$d/A3"
    #mv "$d/agent.py" "$d/A3/agent.py"

    #extract name of student
    pattern="students/([^/].+)"

    if [[ $d =~ $pattern ]]
    then
      name="${BASH_REMATCH[1]}"

      #copy heuristic test files into student folder
      echo "working on $name ... "
      cp "grader-private.py" "$d/grader-private.py"
      cp "/Users/JaglalLab/Desktop/CSC384/csc384-a3/ta/data/private/train-private-1.txt" "$d/train-private-1.txt"
      cp "/Users/JaglalLab/Desktop/CSC384/csc384-a3/ta/data/private/train-private-1.ind" "$d/train-private-1.ind"
      cp "/Users/JaglalLab/Desktop/CSC384/csc384-a3/ta/data/private/test-private-small-1.txt" "$d/test-private-small-1.txt"
      cp "/Users/JaglalLab/Desktop/CSC384/csc384-a3/ta/data/private/test-private-small-1.ind" "$d/test-private-small-1.ind"
      cp "/Users/JaglalLab/Desktop/CSC384/csc384-a3/ta/data/private/test-private-large-1.txt" "$d/test-private-large-1.txt"
      cp "/Users/JaglalLab/Desktop/CSC384/csc384-a3/ta/data/private/test-private-large-1.ind" "$d/test-private-large-1.ind"

      #tag and record results to outfile
      cd "$d"
      python3 "grader-private.py" "$name" "$outfile"
      cd "../../"
    else echo "error processing files in $d"
    fi
done
