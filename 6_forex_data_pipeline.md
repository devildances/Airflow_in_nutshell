# The Forex Data Pipeline Project using Docker

> This project is contained under *forex* folder

<img src="/files/images/img20.png" height="40%" width="40%" />

This project is divided in 8 different tasks:

- The 1st task will check if the forex currencies are available or not
    - in this part we'll reach a specific URL and verify that URL is accessible or not
- In the 2nd task we can check if the file where the currency is we want to fetch from the URL are specified is available or not
- The 3rd task we'll download the forex rates by executing a Python function
- The 4th task we'll save the forex rates into HDFS
- In the 5th task we'll create a Hive table in order to interact with our rates that are stored in our HDFS
- The 6th task we'll process the forex rates with Spark
    - this part explains how we submit a Spark job from our data pipeline
- The 7th task is to send an email to notify that the data pipeline is done and has been executed
- And finally the 8th task will send a Slack notification



<img src="/files/images/img21.png" height="50%" width="50%" />

On the above image, it's the architecture in which our data pipeline for this project is going to run.


> To start the Airflow we just need to run *start.sh* file by executing `./start.sh` command and always never forget to test our task before we run it on our DAG by run `docker exec -it <airflow_container_id> /bin/bash` to get the connection into Airflow CLI then run `airflow tasks test <DAG_id> <task_id> <start_date>` command.