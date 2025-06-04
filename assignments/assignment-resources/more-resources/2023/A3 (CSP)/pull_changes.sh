#requires rsync  version 2.6.9 

# THIS PART IS JUST PULLING CHANGES
for d in submissions/* ; do
    #make directories
    dir_name=${d/submissions\//$1/}
    dir_name=${dir_name/\//$1}
    echo "WORKING ON: $dir_name"
    mkdir "submissions/$dir_name/A3"
    mv "submissions/$dir_name/futoshiki_csp.py" "submissions/$dir_name/A3/futoshiki_csp.py" 
    mv "submissions/$dir_name/propagators.py" "submissions/$dir_name/A3/propagators.py" 

    # pull changes
    # cd $d
    # git pull
    # cd ../../shared_files/
done


# THIS PART IS JUST PULLING ASSIGNMENT SPECIFIC FILES

#echo "\nAssignment Folder is: $1\n";

# #for d in ../${1}/* ; do

# for d in ../gitlab/* ; do
#     dir_name=${d/\.\.\/gitlab\//$1/}
#     dir_name=${dir_name/\//$1}
#     echo "WORKING ON: $dir_name"
#     cd $d 
#     cp assignment2/*Test.java "../../labs/a2/submissions/$dir_name/"
#     #rsync -avm --include='*.java' -f 'hide,! */' "assignment2/" "../../labs/a2/submissions/$dir_name/"
#     cd ../../shared_files
# done

    # A2

# #     # LAB 1
#     cd $d
#     pwd

#     # # LAB 2
#     # cd $d
#     # pwd
#     # mkdir "../../labs/lab02/submissions/$dir_name"
#     # mkdir "../../labs/lab02/submissions/$dir_name/week2/"
#     # cp -r "lab02/week2/" "../../labs/lab02/submissions/$dir_name/week2/"
#     # #cd ../../shared_files

#     # # LAB 3
#     # #cd $d
#     # mkdir "../../labs/lab03/submissions/$dir_name"
#     # mkdir "../../labs/lab03/submissions/$dir_name/week3/"
#     # cp -r "lab03/week3/" "../../labs/lab03/submissions/$dir_name/week3/"
#     # #cd ../../shared_files

#     # # LAB 4
#     # #cd $d
#     # mkdir "../../labs/lab04/submissions/$dir_name"
#     # mkdir "../../labs/lab04/submissions/$dir_name/assets/"
#     # mkdir "../../labs/lab04/submissions/$dir_name/week4/"
#     # cp -r "lab04/assets/" "../../labs/lab04/submissions/$dir_name/assets/"
#     # cp -r "lab04/week4/" "../../labs/lab04/submissions/$dir_name/week4/"    
#     # #cd ../../shared_files


#     # # LAB 5
#     # #cd $d
#     # mkdir "../../labs/lab05/submissions/$dir_name"
#     # mkdir "../../labs/lab05/submissions/$dir_name/week5/"
#     # cp -r "lab05/week5/" "../../labs/lab05/submissions/$dir_name/week5/"
#     # #cd ../../shared_files

#     # LAB 6
#     #cd $d
#     rm -r "../../labs/lab06/submissions/$dir_name"
#     mkdir "../../labs/lab06/submissions/$dir_name"
#     mkdir "../../labs/lab06/submissions/$dir_name/week6/"
#     cp -r "lab06/week6/" "../../labs/lab06/submissions/$dir_name/week6/"
#     cp -r "lab06/EvaluatorTests.java" "../../labs/lab06/submissions/$dir_name/"
#     cp -r "lab06/Main.java" "../../labs/lab06/submissions/$dir_name/"    
#     cd ../../shared_files

#     # # LAB 7
#     # #cd $d
#     # mkdir "../../labs/lab07/submissions/$dir_name"
#     # mkdir "../../labs/lab07/submissions/$dir_name/week7/"
#     # cp -r "lab07/week7/" "../../labs/lab07/submissions/$dir_name/week7/"
#     # cp -r "lab07/Main.java" "../../labs/lab07/submissions/$dir_name/"    
#     # #cd ../../shared_files

#     # # LAB 8
#     # #cd $d
#     # mkdir "../../labs/lab08/submissions/$dir_name"
#     # mkdir "../../labs/lab08/submissions/$dir_name/week8/"
#     # cp -r "lab08/week8/" "../../labs/lab08/submissions/$dir_name/week8/"
#     # cp -r "lab08/Main.java" "../../labs/lab08/submissions/$dir_name/"    
#     # cd ../../shared_files

# #     # #any java files in here?
# #     # if [[ -n $(find "$d" -type f -name "*.java") ]] 
# #     # then

# #     #     # echo "$(find "$d" -type f -name "Player.java" | wc -l)" 
# #     #     # echo "$(find "$d" -type f -name "AdventureGame.java" | wc -l)"
# #     #     # echo "$(find "$d" -type f -name "AdventureObject.java" | wc -l)"
# #     #     # echo "$(find "$d" -type f -name "Room.java" | wc -l)"

# #     #     # #if yes, get into student folder and remove redundant files                    
# #     #     cd "$d/Assignment1"
# #     #     # rm "AdventureObject.java"
# #     #     # rm "Player.java"
# #     #     # rm "AdventureGame.java"
# #     #     # rm "FormattingException.java"
# #     #     # rm "Passage.java"
# #     #     # rm "PassageTable.java"
# #     #     # rm "Room.java"
# #     #     # rm "GameTroll.java"
# #     #     # rm "NoteTroll.java"
# #     #     # rm "SoundTroll.java"

# #     #     # # copy over supporting java files (hidden and student facing tests, plus pom.xml for GUI tests)  
# #     #     # #rsync -avi --include="*/" --include '*.png' --include '*.xml' --include '*.csv' --include '*.java' --include '*.txt' --exclude '*' ../../../supporting_files/ .
# #     #     # #echo "$1"
# #     #     #cp ../../../supporting_files/*java .
# #     #     #cp -r ../../../supporting_files/SmallGame .
# #     #     #cp -r ../../../supporting_files/TestFiles .
# #     #     #cp -r ../../../supporting_files/Crowther .
# #     #     #cp ../../../supporting_files/Trolls/*java Trolls/
# #     #     #cp ../../../supporting_files/AdventureModel/*java AdventureModel/

# #     #     # compile the files (make sure you are using JAVA 18)   
# #     #     #$JAVA_HOME/bin/javac -Xlint:unchecked -d out/ -sourcepath . -cp ../../../shared_files/junit-platform-console-standalone-1.9.0.jar *.java  2> compile_errors.txt    
# #     #     javac -Xlint:unchecked -d out/ -sourcepath . -cp ../../../../shared_files/junit-platform-console-standalone-1.9.0.jar *.java  2> compile_errors.txt    

# #     #     # run the JUnit tests (make sure you are using JAVA 18)           
# #     #     #$JAVA_HOME/bin/java -jar ../../../shared_files/junit-platform-console-standalone-1.9.0.jar -cp out/ --scan-classpath > junit_test_results.txt        
# #     #     java -jar ../../../../shared_files/junit-platform-console-standalone-1.9.0.jar -cp out/ --scan-classpath > junit_test_results.txt        


# #     #     # continue
# #     #     cd ../../../../shared_files/

# #     # fi

# done
