## Default Configurations of Airflow

When we install and run Airflow for the first time, we get the default configuration.

![Alt text](/files/images/img4.png?raw=true "multi parallel tasks")

Based on the DAG image above, let's say we have that data pipeline with 4 different tasks where task 2 and task 3 depend on task 1 and finally task 4 depends on task 2 and task 3. With the default configuration of Airflow, task 1 will be executed first as soon as task 1 is completed we have task 2 and task 3 where those tasks are on the same level which means they can be executed in parallel but we don't know which task will be executed first because those tasks shared the same priority menas either task 2 or task 3 will be executed and once task 2 and task 3 are completed then task 4 will be executed.

> The default configuration of Airflow makes our tasks are executed sequentially one after the other because the default executor is the **SequentialExecutor**.

We can see the default executor value that is used in our Airflow by running this command:
```bash
airflow config get-value core executor
```



## Scaling with the Local Executor

The SequentialExecutor is extremely useful if we want to debug our data pipelines as our task will be executed one after the other, which makes debuging process easier or if we want to make some experiments. If we want to execute multiple tasks in parallel at the same time and also start scaling AIrflow as we will use it in production then we need 2 things:
- we need to change the database (such as Postgres) that allows us to have multiple reads as well as multiple writes
- the second one is we need to change the executor from SequentialExecutor to **LocalExecutor**
    - the LocalExecutor allows us to execute multiple tasks in parallel at the same time on the same machine

Now we can do that by the following steps:
- open the remote terminal to execute some commands that we need
- refresh our packages
    ```bash
    sudo apt update
    ```
- install postgres
    ```bash
    sudo apt install postgresql
    ```
- specify the password of the user by default, which is postgres
    ```bash
    sudo -u postgres psql
    ```
- once we are inside postgres, then we need to specify a password
    ```sql
    ALTER USER postgres PASSWORD 'postgres';
    ```
- before we connect Airflow with postgres DB, we need to install the extra package postgres inside the virtual environment
    ```bash
    pip install 'apache-airflow[postgres]'
    ```
- once it already installed, we ready to use postgres as the metastore of airflow
    - open the file *airflow.cfg*
    - look for `sql_alchemy_conn` variable
        - we need to change this value by our postgres connection
    - add new value for `sql_alchemy_conn` variable with this format `postgresql+psycopg2://[username]:[password]@[address]/[db_name]`
        ```python
        sql_alchemy_conn = postgresql+psycopg2://postgres:postgres@localhost/postgres
        ```
- check if we are able to reach the database
    ```bash
    airflow db check
    ```
- change the Airflow executor
    - open the file *airflow.cfg*
    - look for `executor` variable
        - we need to change this value from sequential to local so we are enable to execute multiple tasks in parallel
        ```python
        executor = LocalExecutor
        ```
- remember to initialize the Airflow again since we changed the DB
    ```bash
    airflow db init
    ```
- once the new DB already initialized, we have to create a new user
    ```bash
    airflow users create -u admin -p admin -f super -l human -r Admin -e admin@airflow.com
    ```
- now, we ready to run the Airflow with new configuration



## Scaling with the Celery Executor

The LocalExecutor is extremely powerful as we can start scaling Airflow and executing multiple tasks in parallel in very easy way. We just need to configure postgres and change the executor in the configuration file of Airflow with LocalExecutor and we are ready to execute as many tasks as the resources of our single machine allow us to do  but at some point we will be limited. If we have hundreds of tasks to execute, obviously a single machine won't be enough at some point and that's where we need to find another executor in order to scale as much as we need. There are 2 executors to do this, the first one is the **CeleryExecutor** and the second one is **KubernetesExecutor**.

> One very important thing that we have to remember is all those executors use a Queue in order to execute our tasks in the right order. Each time a task is triggered in Airflow, that task is first added into a Queue and then once Airflow is ready to execute it and that task is pulled out from the Queue and being executed. **So having a Queue is extremely important in order to keep the order in which our tasks should be executed.**

The **CeleryExecutor** is a distributed task system and with it we are able to spread our work and able to execute our tasks among multiple machines. Basically, our tasks are executed in workers (machines) and the more workers we have then the more tasks we'll be able to execute.


![Alt text](/files/images/img5.png?raw=true "multinode workers")

Let's say we have the architecture as above with the CeleryExecutor, first we have *Node 1* with the Web server and the Scheduler of Airflow are running then *Node 2* where the Metadatabase of Airflow is running (Postgresql, MySQL, or etc.). Instead of having the Queue inside the Executor, we put it outside from the Executor in *Node 3* and it is a third-party tool (Redis, RabbitMQ, etc.) as an in-memory database that we can use it as a Queue system or as message broker system. With the CeleryExecutor, each time we execute a task then it will be pushed first in *Node 3* and a worker will pull the task from *Node 3* in order to execute it.

*Node 4*, *Node 5* and *Node 6* are corresponding to different workers (machines) where our tasks will be executed. In worker nodes we have 1 parameter named *worker_concurrency* with the value of Integer, that parameter defines the number of tasks that we can execute at most in each of our workers and it's defined inside the configuration file of Airflow.

This is how the task is executed:
1. We have task named T1 in *Node 1* (the Scheduler) ready to be triggered
2. T1 will be pushed inside *Node 3*
3. Once the task is inside *Node 3*, one of the Workers will pull out T1 from *Node 3*
4. In Worker, T1 is ready to be executed
5. This process goes over and over again forr all of the tasks

> Therefore, we have to make sure that all of our machines share the same dependencies. For example if we have a task interacting with AWS then we have to make sure that *boto3* is installed on all of our machines otherwise we'll end up with the error.

Here are the following steps to enable CeleryExecutor:
- First, we need to install the extra package Celery
    ```bash
    pip install 'apache-airflow[celery]'
    ```
- We need to have in-memory database, in this case we'll install Redis
    ```bash
    sudo apt update
    sudo apt install redis-server
    ```
    - Once Redis already installed, we need to modify its configuration in order to use it as a service
        - open the Redis configuration file
        ```bash
        sudo nano /etc/redis/redis.conf
        ```
        - change the value of `supervised` from `no` to `systemd`
        ```bash
        supervised systemd
        ```
        - exit the file using ctrl+X and save the file with Y
    - Start the Redis service
    ```bash
    sudo systemctl restart redis.service
    ```
    - Check if Redis is running or not
    ```bash
    sudo systemctl status redis.service
    ```
        - hit Q to exit
    - Now our Redis already installed, configured and ready to use
- Next we configure the CeleryExecutor with Airflow
    - Open *airflow.cfg* file
        - change the Airflow executor
            - look for `executor` variable
            - we need to change this value to celery so we are enable to run on multiple machines
            ```python
            executor = CeleryExecutor
            ```
        - make sure we don't use SQLite connection for `sql_alchemy_conn` variable
        - change the Celery broker URL
            - look for `broker_url` variable
            - this variable is used by Celery in order to push the tasks to the Redis message broker
            - we need to specify the connection corresponding to our Redis instance
            - the format of the value is ```redis://[host]:[port]/[db_name]```
            ```python
            broker_url = redis://localhost:6379/0
            ```
        - change the Celery result_backend
            - look for `result_backend` variable
            - basically each time a task is completed, some metadata related to the execution of that task in the contect of Celery will be stored and that's why we need o specify the `result_backend` which is actually the Postgres DB (since we use postgres for our metabase DB) that we use with Airflow
            - remove the default value of `result_backend` and put same connection as the SQL Alchemy connection `sql_alchemy_conn` variable but without psycopg2
            ```python
            result_backend = db+postgresql://postgres:postgres@localhost/postgres
            ```
- Since we'll interact with Redis from Airflow then we need  to install extra package
    ```bash
    pip install 'apache-airflow[redis]'
    ```
- Now we have successfully configured Airflow with the CeleryExecutor


### The Celery Flower

One coll feature that Airflow brings by default with the Celery executor is **Flower**. It is the User Interface that allows us to monitor our workers that will be used by Airflow and Celery executor where our tasks will be executed.

We can start The Celery Flower by the following:
- Open new terminal
- Type this command to activate it
    ```bash
    airflow celery flower
    ```
- By default, it's running on the port 5555
- Open our browser and go to localhost:5555

> If you get the error while trying to execute Flower command, probably because the Celery version you installed is not supported by the current version of Airflow so you need to downgrade the version of the Celery by running this command `pip install --upgrade apache-airflow-providers-celery==2.0.0`


### Add New Worker to Airflow Instance

This is how we add new worker to our Airflow instance:
- Open new terminal
- Use this command to add new worker in our instance
    ```bash
    airflow celery worker
    ```
    - by executing this command, we are specifying that the current machine where this command is executed is a worker and so that machine can be used to execute our tasks
    - in the real scenario, we'll actually execute this command on each machine that we want to add to our Selery cluster