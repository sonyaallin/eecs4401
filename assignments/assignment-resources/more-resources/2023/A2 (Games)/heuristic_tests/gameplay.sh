#!/bin/bash

#change outfile to name of file you want to write to (to hold results)
outfile="/Users/JaglalLab/Desktop/heuristic_tests/grades.csv"
#change scorefile to name of file you want to write to (to hold raw scores)
scorefile="/Users/JaglalLab/Desktop/heuristic_tests/scores.csv"
#change errorfile to name of file you want to write to (to hold list of exceptions)
errorfile="/Users/JaglalLab/Desktop/heuristic_tests/errors.csv"

#change DIRECTORIES to name of directory with student submissions
DIRECTORIES=students/*
echo "utorid, wins, losses, ties" > "$outfile"
echo "utorid, score1, score2, depth, start" > "$scorefile"
echo "utorid, error encountered" > "$errorfile"

for d in $DIRECTORIES
do
    #uncomment to make subdirectory for student submissions and move files
    mkdir "$d/A3"
    #mv "$d/agent.py" "$d/A3/agent.py"

    #extract name of student
    pattern="students/([^/].+)"

    if [[ $d =~ $pattern ]]
    then
      name="${BASH_REMATCH[1]}"

      #copy heuristic test files into student folder
      echo "working on $name ... "
      cp "gameplay/agent_TA_default.py" "$d/A3/agent_TA_default.py"
      cp "gameplay/agent_TA_student.py" "$d/A3/agent_TA_student.py"
      cp "gameplay/game_play_test.py" "$d/A3/game_play_test.py"
      cp "gameplay/mancala_shared.py" "$d/A3/mancala_shared.py"
      cp "gameplay/mancala_game.py" "$d/A3/mancala_game.py"

      #play games and record results to outfile
      cd "$d/A3/"
      python3 "game_play_test.py" "$name" "$outfile" "$scorefile" "$errorfile"
      cd "../../../"
    else echo "error processing files in $d"
    fi
done
