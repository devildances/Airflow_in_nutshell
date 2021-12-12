## I. How to Start

- Install Virtual Machine on our local (e.g. VirtualBox)
- Download Linux distribution (Ubuntu) that will be running in VirtualBox
- Start the VM, open our web browser and go to *localhost:8080* to open the Airflow UI
- Access the VM in SSH and connect VS Code through it
    - Open our terminal and type ```ssh -p 2222 airflow@localhost```
    - Type `yes` if it asks for connecting
    - Then we need to enter the password `airflow`
    - At this point we're inside the VM connected through the user **airflow**
    - Hit *Control+D* to exit the VM
- set up Visual Studio Code to edit files/folders in the VM
    - Open VS Code
    - Click on "Extensions"
    - In the search bar on the top, look for "remote ssh" and Install it
    - Once the plugin is installed, open it by hitting
        - *Cmd-P* (on Mac)
        - *F1* (on Windows)
    - Type `>remote-ssh`
    - Then hit enter, and select *"Add New SSH host..."*
    - Enter the following command ```ssh -p 2222 airflow@localhost``` and hit enter
    - Select the first proposition for the SSH config file
    - Now the connection has been added, open the plugin again
        - *Cmd-P* (on Mac)
        - *F1* (on Windows)
    - Type `>remote-ssh` Then choose *"localhost"* by hitting enter
    - A new Visual Studio Code window opens, type the password `airflow`
    - And **WE ARE CONNECTED!**
- Installing Airflow 2.0
    - Open new terminal in our VS Code
    - Create new python virtual environment using `venv` command
        - ```python3 -m venv sandbox```
    - Activate the virtual environment that already created
    - Install Wheel package in our virtual environment using pip
        - ```pip install wheel```
    - Now we need to install Airflow in our virtual environment
        ```bash
        AIRFLOW_VERSION=2.2.2
        PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
        CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-no-providers-${PYTHON_VERSION}.txt"
        pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
        ```
    - Run initiating db in order to initiate the Metastore of Airflow as well as generating some files and folders needed by Airflow
        - ```airflow db init```
    - After all commands already executed, we'll have a folder named **airflow** that contains some folders and files
        - airflow.cfg : this file is the configuration file of Airflow
        - airflow.db : this file is corresponding to the database that we use by default which is SQLite
        - logs : this folder let us to check the logs of our tasks of the Scheduler and so on
        - unittests.cfg : this file can be pretty useful if we want to test some configuration of our Airflow without impacting our Airflow instance
        - webserver_config.py : this file is useful to configure the Web server
    - Create a user using Airflow CLI
        - ```airflow users create -u admin -p admin -f super -l human -r Admin -e admin@airflow.com```
            - -u means the username
            - -p means the password for the username
            - -f means the firstname
            - -l means the lastname
            - -r means the role for the username
            - -e means the email address
    - Start the User Interface of Airflow
        - ```airflow webserver```
    - Now go to the web browser and open *localhost:8080* to check that our Airflow UI is working
    - **Important commands in Airflow**
        - ```airflow db init```
            - this command is used for initiating the Metastore of Airflow as well as generating some files and folders needed by Airflow
            - we will execute this command only once and shouldn't use it anymore
        - ```airflow db upgrade```
            - we will execute this command when we want to upgrade Airflow version
        - ```airflow db reset```
            - this command is really **dangerous**
            - make sure that we know what we're doing before executing this command as we'll lose everything
            - only use this command if we want to make some experiments and **don't use it in production**
        - ```airflow webserver```
            - this command is used to start the User Interface of Airflow
        - ```airflow scheduler```
            - this command is used to start the scheduler of Airflow
            - the Scheduler is in charge of scheduling our data pipelines and so our tasks
        - ```airflow dags list```
            - this command is used to get all list of DAGs that Airflow has taken into account
        - ```airflow tasks list <DAG_name>```
            - this command is used to know the tasks in specific DAG
        - ```airflow dags trigger -e <yyyy-mm-dd> <DAG_name>```
            - this command allows us to trigger our data pipeline with the specific execution date from the CLI of Airflow


> To remove all of the example DAGs in our Airflow, just open *airflow.cfg* file, look for `load_examples` variable then change the value to `False`,  after that save the file and restart the Airflow also the Scheduler.



## II. How to Create a Data Pipeline

- Open our VS Code and remote to our VirtualBox engine
- Activate the python virtual environment that already created before
- Go to the airflow folder in the directory
- Access it through the Explorer on our VS Code
- Create new folder named **dags** if we don't have on it using `mkdir` command
    - In this folder that we'll put the python files corresponding to our data pipelines
- Create new python file under **dags** folder
    -  This file is where we will define our DAG/Data Pipeline
    - The minimum code that we heve to put each time we create a new data pipeline Airflow are:
        - import the DAG object
            ```python
            from airflow.models import DAG
            ```
        - import datetime object that will be useful in order to define a date that we need to specify
        - instantiate our *DAG*
            - first we need to do is define the DAG id
                - the DAG id **must be unique** among all of our DAGs
                - each data pipeline in Airflow must have a unique DAG id
            - next we need to define the scheduling interval in our DAG object
                - it indicates the frequency at which our data pipeline will be triggered
            - we have to define when the data pipeline will stop being scheduled and when ti will be triggered using `catchup` parameter
            - finally, initialize our DAG object
        - define the *tasks*/*operators* under our DAG object
            - an operator is a task in our data pipeline or an operator defines one task in our data pipeline
                - **IMPORTANT : 1 operator for 1 task, don't put 1 operator for 2 tasks or more!!**
                - e.g. the PythonOperator execute only 1 python function (cleaning data or processing data but not both of them in one operator), if we want to execute/run 2 tasks then separate them in different PythonOperator
        - define the *default arguments* on top of our DAG object as dictionary data types and inside it we have to specify all the arguments that will be common to all our our tasks/operators in our data pipeline
            - define the start date in the default arguments
                - the value of this parameter is actually when our data pipeline will start being scheduled



### DAG Scheduling

In Airflow, there is one concept that we absolutely need to remember which is how our DAGs are scheduled. Whenever we define a DAG, there are 2 arguments that we will always define:

- `start_date`
    - this parameter is defining when our DAG will start being scheduled
- `schedule_interval`
    - this parameter is defining the frequency at which our data pipeline will be triggered

> There is something that we absolutely need to remember is that our data pipeline will be effectively triggered once the `start_date` plus the `schedule_interval` is elapsed.



## III. How to Test New Task

Each time we add a new task in our data pipeline, there is always one thing that we have to do and that is testing our task. To do this, there is a specific command as below :

```airflow tasks test <DAG id> <task id> <execution date with format yyyy-mm-dd>```

The above command allows us to test a specific task without checking for the dependencies neither storing any metadata related to that task.



## IV. Backfilling and Catchup

Let's imagine that we make a mistake or something issue in specific task and specific date/time in our data pipeline, then backfilling and catchup concepts in Airflow are very important to help us resolve the issue.

We have to know that automatically Airflow will run all the non-triggered DAGruns between the time where we pause and the time where we have resume our DAG so all the non-triggered DAGruns will be automatically by Airflow in order to catch up all the non-triggered DAGruns between that period of time. This is controlled by a very simple paramater but very powerful called `catchup` which is set to *True* by default for all of our DAGs.

> If we initiate the value of `catchup` parameter as *False* in our DAG and after several times we change the value with *True* then once we running the DAG again it will trigger all the non-triggered DAGruns starting from the latest execution_date not from start_date. Non-triggered DAGruns will be automatically triggered by Airflow starting from the start_date if it is the first time that we schedule our data pipeline otherwise will be triggered from the latest execution_date. but we can change it by going to the *Browse* menu in UI of Airflow and selecting the *DAG Runs* sub-menu then delete all records related to the DAG that we want to restart.