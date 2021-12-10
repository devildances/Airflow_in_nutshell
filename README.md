# APACHE AIRFLOW

Airflow is an orchestrator, not a processing framework, process our gigabytes of data outside of Airflow (i.e. We have a Spark cluster, we use an operator to execute a Spark job, the data is processed in Spark).



## Core Components of Airflow

- Web server
    - Flask server with Gunicorn serving the UI for airflow
- Scheduler
    - Daemon in charge of scheduling workflows
    - This is truly the health of airflow and we have to take care of it
- Metastore
    - Database where metadata are stored
    - Usually we'll use Postgres as it is recommended database to use with Airflow but we can use MySQL or Oracle as long as the database is compatible with SQLAlchemy
- Executor
    - Class defining how our tasks should be executed
    - If we want to execute our tasks on the same machine by creating subprocesses then we will use the local executor
    - If we want to execute our tasks using a Celery cluster then we'll use the Celery executor
- Worker
    - Process/sub process executing our task

> The scheduler schedules your tasks, the web server serves the UI, the database stores the metadata of Airflow. A DAG is a data pipeline, an Operator is a task.



## Airflow Architecture

### One Node Architecture

![Alt text](/files/images/img1.png?raw=true "One Node Architecture")

- In this architecture we'll have the Web erver, The Scheduler, the Metastore and the Executor running inside a single machine
- The Web server will fetch some metadata coming from the Metastore then the Scheduler will be able to talk with the Metastore and the Executore in order to send tasks that we want to execute and the Executor will update the status of the tasks in the Metastore
- And we also have a Queue inside the Executor where that Queue is used in order to define the order in which our tasks will be executed
- This architecture is perfect if we want to do some experiments with Airflow or if we have a limited number of tasks that we want to execute


### Multi Nodes Architecture (Celery)

![Alt text](/files/images/img2.png?raw=true "Multi Nodes Architecture")

- In this architecture we have a **Node 1** with the Web server, the Scheduler and the Executor but we have another node where the Metastore and the Queue are running
- Here the Queue is actually external to the executor not like in the single node architecture so this Queue will be the third party like RabbitMQ or Redis
- In here also we'll have multiple multiple nodes, multiple machines, where on each machine will have an Airflow worker running and those Airflow workers will be used in order to execute our tasks
    - So our tasks will not be executed on the **Node 1** or **Node 2** but will be spread among the worker nodes in order to execute as many tasks as we want



## Directed Acyclic Graph (DAG)

![Alt text](/files/images/img3.png?raw=true "DAG")

The DAG is data pipeline in Airflow and it's a graph like the image above with nodes corresponding to our tasks and Edges corresponding to the dependencies in Airflow. What we'll have basically is that as soon as our data pipeline/DAG is triggered, all the tasks will bexecuted in the order as given from the dependencies.



## Types of Operators

1. Action Operators : Execute an action, corresponding to all operators executing a function
    - PythonOperator
    - BashOperator
    - so on
2. Transfer Operators : Transfer data, those are related to any operator transferring data from a source to a destination
3. Sensors : wait for a condition to be met, those are used in order to wait for something to happen before moving to the next task
    - e.g. we want to wait for a SQL record to be updated in our database then we will use the Sensors



## The Providers - [LINK](https://airflow.apache.org/docs/apache-airflow-providers/packages-ref.html)

Apache Airflow allows us to interact with a ton of different tools such as Spark, AWS, Databrick and etc. In fact, Airflow has more than 700 operators. Airflow 2.0 is composed of multiple separated but connected packages with a Core package apache-airflow and providers.

A provider is an independent python package that brings everything we need to interact with a service or a tool such as Spark or AWS. It contains connection types, operators, hooks and so on.

By default, [some operators](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/index.html) are pre installed by default such as the PythonOperator and the BashOperator but for the others you will have to install the corresponding prodiver.

Now, we can install only the operators we need (no more 200 different dependencies to deal with whereas we just use 3 or 4 operators). If there is a new version of our operator, we just have to update the provider and not our Airflow instance like the version before. On top of that, it's never been easy to create our own provider.

Also, to know which providers are already installed, type ```airflow providers list```.



# AIRFLOW IS NOT A DATA STREAMING SOLUTION NEITHER DATA PROCESSING FRAMEWORK

So if we want to process data every second then **don't use Airflow** because it's not the purpose of Airflow and also Airflow it's not same with Spark so if we want to process terabytes of data then **do that in Airflow**. If we want to process terabytes of data, we'll use the Spark submit operator and that operator will send Spark job where the terabytes of data will be processed inside Spark and not inside Airflow otherwise the memory of Airflow will be exploded.



## How to Start

- Install Virtual Machine on our local (e.g. VirtualBox)
- Download Linux distribution (Ubuntu) that will be running in VirtualBox
- Start the VM, open our web browser and go to *localhost:8080* to go through the Airflow UI
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
    - Activate the venv that already created
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
    - Start the User Interface of Airflow
        - ```airflow webserver```
    - Now go to the web browser and open *localhost:8080* to check that our Airflow UI is working
    - Create a user using Airflow CLI
        - ```airflow users create -u admin -p admin -f super -l human -r Admin -e admin@airflow.com```
        - -u means the username
        - -p means the password for the username
        - -f means the firstname
        - -l means the lastname
        - -r means the role for the username
        - -e means the email address
    - **Important commands in Airflow**
        - ```airflow db init```
            - this command is used for initiating the Metastore of Airflow as well as generating some files and folders needed by Airflow
            - we will execute this command only once and shouldn't use it anymore
        - ```airflow db upgrade```
            - we will execute this command when we want to upgrade Airflow version
        - ```airflow db reset```
            - this command is really **dangerous**
            - make sure that we know what we're doing before executing this command as we'll lose everything
            - only use this command if we want to make some experiments and don't use it in production
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



## How to Crete a Data Pipeline

- Open our VS Code and remote to our VirtualBox engine
- Activate the python virtual environment that already created before
- Go to the airflow folder in the directory
- Access it through the Explorer on our VS Code
- Create new folder named **dags** if we don't have on it using `mkdir` command
    - In this folder that we'll put the python files corresponding to our data pipelines
- Create new python file under **dags** folder
    -  This file is where we will define our DAG/Data Pipeline
    - The minimum code that we heve to put each time we create a new data pipeline Airflow are
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
                - e.g. the PythonOperator execute only 1 python function (cleaning data or processing data but not both of them in one operator), if we want to execute/run 2 tasks then seperate them in different PythonOperator
        - define the *default arguments* on top of our DAG object as dictionary data types and inside it we have to specify all the arguemnts that will be common to all our our tasks/operators in our data pipeline
            - define the start date in the default arguments
                - the value of this parameter is actually when our data pipeline will start being scheduled



### DAG Scheduling

In Airflow, there is one concept that we absolutely need to remember which is how our DAGs are scheduled. Whenever we define a DAG, there are 2 arguments that we will always define:

- `start_date`
    - this parameter is defining when our DAG will start being scheduled
- `schedule_interval`
    - this parameter is defining the frequency at which our data pipeline will be triggered

> There is something that we absolutely need to remember is that our data pipeline will be effectively triggered once the `start_date` plus the `schedule_interval` is elapsed.



## How to Test New Task

Each time we add a new task in our data pipeline, there is always one thing that we have to do and that is testing our task. To do this, there is a specific command as below :

```airflow tasks test <DAG id> <task id> <execution date with format yyyy-mm-dd>```

The above command allows us to test a specific task without checking for the dependencies neither storing any metadata related to that task.



## Backfilling and Catchup

Let's imagine that we make a mistake or something issue in specific task and specific date/time in our data pipeline, then backfilling and catchup concepts in Airflow are very important to help us resolve the issue.

We have to know that automatically Airflow will run all the non-triggered DAGruns between the time where we pause and the time where we have resume our DAG so all the non-triggred DAGruns will be automatically by Airflow in order to catch up all the non-triggered DAGruns between that period of time. This is controlled by a very simple paramater but very powerful called `catchup` which is set to *True* by default for all of our DAGs.

> If we initiate the value of `catchup` parameter as *False* in our DAG and after several times we change the value with *True* then once we running the DAG again it will trigger all the non-triggered DAGruns starting from the latest execution_date not from start_date. Non-triggered DAGruns will be automatically triggered by Airflow starting from the start_date if it is the first time that we schedule our data pipeline otherwise will be triggered from the latest execution_date. but we can change it by going to the *Browse* menu and selecting the *DAG Runs* sub-menu then delete all records related to the DAG that we will restart.