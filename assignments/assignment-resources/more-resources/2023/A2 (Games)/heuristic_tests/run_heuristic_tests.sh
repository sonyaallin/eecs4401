#!/bin/bash

# #change outfile to name of file you want to write to (to hold results)
# outfile="/Users/JaglalLab/Desktop/heuristic_tests/grades.csv"
# #change scorefile to name of file you want to write to (to hold raw scores)
# scorefile="/Users/JaglalLab/Desktop/heuristic_tests/scores.csv"
# #change errorfile to name of file you want to write to (to hold list of exceptions)
# errorfile="/Users/JaglalLab/Desktop/heuristic_tests/errors.csv"

#change DIRECTORIES to name of directory with student submissions
DIRECTORIES=submissions/*
# echo "utorid, wins, losses, ties" > "$outfile"
# echo "utorid, score1, score2, depth, start" > "$scorefile"
# echo "utorid, error encountered" > "$errorfile"

for d in $DIRECTORIES
do
    #uncomment to make subdirectory for student submissions and move files
    #mkdir "$d/A3"
    #mv "$d/agent.py" "$d/A3/agent.py"

    #extract name of student
    pattern="submissions/([^/].+)"

    if [[ $d =~ $pattern ]]
    then
      name="${BASH_REMATCH[1]}"

      #copy heuristic test files into student folder
      echo "working on $name ... "
      cp "supplementary_files/agent_TA.py" "$d/A3/agent_TA.py"
      cp "supplementary_files/agent_student.py" "$d/A3/agent_student.py"
      cp "supplementary_files/mancala_gui.py" "$d/A3/mancala_gui.py"
      cp "supplementary_files/mancala_game.py" "$d/A3/mancala_game.py"

      #play games and record results to outfile
      cd "$d/A3/"
      python3 mancala_gui.py -a agent_student.py -b agent_TA.py -d 6 -l 4
      python3 mancala_gui.py -a agent_student.py -b agent_TA.py -d 6 -l 5
      python3 mancala_gui.py -a agent_student.py -b agent_TA.py -d 6 -l 6
      python3 mancala_gui.py -a agent_student.py -b agent_TA.py -d 6 -l 7
      python3 mancala_gui.py -a agent_student.py -b agent_TA.py -d 6 -l 8
      python3 mancala_gui.py -b agent_student.py -a agent_TA.py -d 6 -l 4
      python3 mancala_gui.py -b agent_student.py -a agent_TA.py -d 6 -l 5
      python3 mancala_gui.py -b agent_student.py -a agent_TA.py -d 6 -l 6
      python3 mancala_gui.py -b agent_student.py -a agent_TA.py -d 6 -l 7
      python3 mancala_gui.py -b agent_student.py -a agent_TA.py -d 6 -l 8
      cp scores.txt "../../../scores-$name.txt"

      cd "../../../"

    else echo "error processing files in $d"
    fi
done

