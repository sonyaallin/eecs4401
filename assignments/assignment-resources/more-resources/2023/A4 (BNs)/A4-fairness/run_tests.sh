for d in remarks/*/ ; do
    #echo "$d"
    cleaned=${d//remarks/} 
    cleaned=${cleaned//\//} 
    echo $cleaned
    python3.10 A4_tests.py all "$cleaned"
done
