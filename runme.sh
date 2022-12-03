#!/bin/bash

echo "Enter username: "
read user_name
#echo $user_name

echo "Enter Password: "
echo "Type password: (Keep typing, it is hidden)"
read -s pass_name

#current_dir = $PWD

echo $PWD
nohup python3 router.py &

echo $pass_name | ./pass.sh ssh -o StrictHostKeyChecking=no $user_name@rasp-031.berry.scss.tcd.ie "nohup python3 $PWD/router.py >/dev/null 2>&1 &"
echo $pass_name | ./pass.sh ssh -o StrictHostKeyChecking=no $user_name@rasp-040.berry.scss.tcd.ie "nohup python3 $PWD/producer.py train 1 >/dev/null 2>&1 &"
echo $pass_name | ./pass.sh ssh -o StrictHostKeyChecking=no $user_name@rasp-041.berry.scss.tcd.ie "nohup python3 $PWD/producer.py metro 1 >/dev/null 2>&1 &"
echo $pass_name | ./pass.sh ssh -o StrictHostKeyChecking=no $user_name@rasp-042.berry.scss.tcd.ie "nohup python3 $PWD/producer.py bus 1   >/dev/null 2>&1 &"
echo $pass_name | ./pass.sh ssh -o StrictHostKeyChecking=no $user_name@rasp-043.berry.scss.tcd.ie "nohup python3 $PWD/producer.py tram 1  >/dev/null 2>&1 &"
echo $pass_name | ./pass.sh ssh -o StrictHostKeyChecking=no $user_name@rasp-044.berry.scss.tcd.ie "nohup python3 $PWD/producer.py taxi 1  >/dev/null 2>&1 &"

