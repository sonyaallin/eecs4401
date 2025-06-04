#!/bin/bash
#script to move files into subdirectories
DIRECTORIES=repos/*
for d in $DIRECTORIES
do
    echo $d
    if [[ -f "$d/Assignment3/agent_competition.py" ]]    
    then
        echo "$d/agent_competition.py" 
        cp "$d/agent_competition.py" "competition/${d//submissions\//}-agent.py"       
    fi

    if [[ -f "$d/Assignment3/agent.py" ]]    
    then
        echo "$d/agent.py" 
        #cp "$d/agent_competition.py" "competition/${d//submissions\//}-agent.py"       
    fi

done
