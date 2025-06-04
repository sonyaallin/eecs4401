for d in students_sel/* ; do
    # This part will make directories for all student submissions and move the solution file and test problem set into the directories
    echo "$d"
    #mkdir "$d/A1/"
    #mv "$d/solution.py" "$d/A1/"

    # This part will make directories for all student submissions and move the solution file and test problem set into the directories
    #echo "${d%?}_result.txt"
    #ls "$d/A1/*"
    pwd
    cp "$d/A1/_results.txt" "${d%?}_results.txt"
    #mv "${d%?}_results.txt" "../results"
    
    # ../results/${d%?}_results.txt"
done
