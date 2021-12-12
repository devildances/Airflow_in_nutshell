# APACHE AIRFLOW

Airflow is an orchestrator, not a processing framework, process our gigabytes of data outside of Airflow (i.e. We have a Spark cluster, we use an operator to execute a Spark job, the data is processed in Spark).



## I. Core Components of Airflow

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

> The scheduler schedules our tasks, the web server serves the UI, the database stores the metadata of Airflow. A DAG is a data pipeline, an Operator is a task.



## II. Airflow Architecture

### II.1. One Node Architecture

![Alt text](/files/images/img1.png?raw=true "One Node Architecture")

- In this architecture we'll have the Web server, The Scheduler, the Metastore and the Executor running inside a single machine
- The Web server will fetch some metadata coming from the Metastore then the Scheduler will be able to talk with the Metastore and the Executore in order to send tasks that we want to execute and the Executor will update the status of the tasks in the Metastore
- And we also have a Queue inside the Executor where that Queue is used in order to define the order in which our tasks will be executed
- This architecture is perfect if we want to do some experiments with Airflow or if we have a limited number of tasks that we want to execute


### II.2. Multi Nodes Architecture (Celery)

![Alt text](/files/images/img2.png?raw=true "Multi Nodes Architecture")

- In this architecture we have a **Node 1** with the Web server, the Scheduler and the Executor but we have another node where the Metastore and the Queue are running
- Here the Queue is actually external to the executor not like in the single node architecture so this Queue will be the third party like RabbitMQ or Redis
- In here also we'll have multiple multiple nodes, multiple machines, where on each machine will have an Airflow worker running and those Airflow workers will be used in order to execute our tasks
    - So our tasks will not be executed on the **Node 1** or **Node 2** but will be spread among the worker nodes in order to execute as many tasks as we want



## III. Directed Acyclic Graph (DAG)

![Alt text](/files/images/img3.png?raw=true "DAG")

The DAG is data pipeline in Airflow and it's a graph like the image above with nodes corresponding to our tasks and Edges corresponding to the dependencies in Airflow. What we'll have basically is that as soon as our data pipeline/DAG is triggered, all the tasks will be executed in the order as given from the dependencies.



## IV. Types of Operators

1. Action Operators : Execute an action, corresponding to all operators executing a function
    - PythonOperator
    - BashOperator
    - so on
2. Transfer Operators : Transfer data, those are related to any operator transferring data from a source to a destination
3. Sensors : wait for a condition to be met, those are used in order to wait for something to happen before moving to the next task
    - e.g. we want to wait for a SQL record to be updated in our database then we will use the Sensors



## V. The Providers - [LINK](https://airflow.apache.org/docs/apache-airflow-providers/packages-ref.html)

Apache Airflow allows us to interact with a ton of different tools such as Spark, AWS, Databrick and etc. In fact, Airflow has more than 700 operators. Airflow 2.0 is composed of multiple separated but connected packages with a Core package apache-airflow and providers.

A provider is an independent python package that brings everything we need to interact with a service or a tool such as Spark or AWS. It contains connection types, operators, hooks and so on.

By default, [some operators](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/index.html) are pre installed by default such as the PythonOperator and the BashOperator but for the others we will have to install the corresponding provider.

Now, we can install only the operators we need (no more 200 different dependencies to deal with whereas we just use 3 or 4 operators). If there is a new version of our operator, we just have to update the provider and not our Airflow instance like the version before. On top of that, it's never been easy to create our own provider.

Also, to know which providers are already installed, type ```airflow providers list```.



# AIRFLOW IS NOT A DATA STREAMING SOLUTION NEITHER DATA PROCESSING FRAMEWORK

So if we want to process data every second then **don't use Airflow** because it's not the purpose of Airflow and also Airflow it's not same with Spark so if we want to process terabytes of data then **don't do that in Airflow**. If we want to process terabytes of data, we'll use the Spark submit operator and that operator will send Spark job where the terabytes of data will be processed inside Spark and not inside Airflow otherwise the memory of Airflow will be exploded.