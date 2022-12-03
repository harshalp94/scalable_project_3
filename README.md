Scalable Group 15 code base   
Added a runme.sh -  
Need to run runme.sh - Add permission(if needed) to make this file executable   
for eg: - chmod +x pass.sh  
          chmod +x runme.sh  
pass.sh - Inputs the password when ssh command prompts for entering password  
runme.sh - Starts the router and producers on separate nodes to start up the system  
Raspberry pi id - 30, and 31 are used as router and backup router respectively.   
Raspberry pi id - 40-44 are used as producers for producing the train, metro, bus, tram and taxi data respectively.  
Once the system has started - Login to raspberry pi and navigate to the code folder and run  
python3 client.py  
This will create a prompt for user to enter inputs and get data according to the inputs.   

The system can be manually started as well,   
For example, one can navigate to code folder to start the respective files  
on PI id 30 - python3 router.py  
on PI id 31 - python3 router.py  
on PI id 40 - python3 producer.py train 1 (1 represents the train id - it should be an integer > 0)  
on PI id 41 - python3 producer.py bus 1  
on PI id 42 - python3 producer.py tram 1  
on PI id 43 - python3 producer.py metro 1  
on PI id 44 - python3 producer.py taxi 1    
on PI id 45 - python3 client.py  



