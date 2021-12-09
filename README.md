# APACHE AIRFLOW

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


# AIRFLOW IS NOT A DATA STREAMING SOLUTION NEITHER DATA PROCESSING FRAMEWORK.

So if we want to process data every sevond then **don't use Airflow** because it's not the purpose of Airflow and also Airflow it's not same with Spark so if we want to process terabytes of data then **do that in Airflow**. If we want to process terabytes of data, we'll use the Spark submit operator and that operator will send Spark job where the terabytes of data will be processed inside Spark and not inside Airflow otherwise the memory of Airflow will be exploded.