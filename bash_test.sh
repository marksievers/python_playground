#!/bin/bash
########## FOR LOOP
for i in "foo" "bar" "baz" "quz" "foobar"
do
   echo "Welcome $i times"
done

########## IF STATEMENT
proceed = "y"

if [ "$proceed" == "y" ] then
	echo "Its yes!"
elif [ "$proceed" == "good" ] then
    echo "Its good!"
else
	echo "Skipping with no changes."
fi

########### READ INPUT, USE VARIABLE WITH DEFAULT
# -p for no new line
read -p "Enter db user name (default is andsome): " db_user
db_user=${db_user:-andsome}
echo "Recreating $db_user database"

############ ECHO
#use -e to use escape codes
echo -e "Done provisioning Issues\n"
#use -n to NOT output new line
echo -n "This should only be run when you intend to remove ALL data (see data_import/readme.txt)! 'y' to proceed or anything else to skip: "