#requires rsync  version 2.6.9 

for d in submissions/* ; do

    dirname=${d/submissions\///}
    dirname=${dirname/\//}
    echo "WORKING ON: $dirname"

    #any java files in here?
    if [[ -n $(find "$d" -type f -name "*.py") ]] 
    then

        cd "$d/A3/"
        pwd
        ls ../../../supporting_files/

        # copy over supporting java files (hidden and student facing tests, plus pom.xml for GUI tests)  
        rsync -avi --ignore-existing --include="*/" --include '*.png' --include '*.xml' --include '*.csv' --include '*.py' --include '*.txt' --exclude '*' ../../../supporting_files/ .
        cp "../../../supporting_files/A2_test_cases_aux.py" .
        rm "scores.txt"

        python3 "A2_test_cases_aux.py" "${dirname}" > "${dirname}_result.txt"

        # continue
        cd ../../../

    fi

done
