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


# AIRFLOW IS NOT A DATA STREAMING SOLUTION NEITHER DATA PROCESSING FRAMEWORK

So if we want to process data every sevond then **don't use Airflow** because it's not the purpose of Airflow and also Airflow it's not same with Spark so if we want to process terabytes of data then **do that in Airflow**. If we want to process terabytes of data, we'll use the Spark submit operator and that operator will send Spark job where the terabytes of data will be processed inside Spark and not inside Airflow otherwise the memory of Airflow will be exploded.


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
        PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
        CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-main/constraints-${PYTHON_VERSION}.txt"
        pip3 install "apache-airflow-providers-google" --constraint "${CONSTRAINT_URL}"
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