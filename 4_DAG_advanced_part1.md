## 1. start_date and schedule_interval parameters

- `start_date` : the date from which tasks of our DAG can be scheduled and triggered
- `schedule_interval` : the interval of time from the min (`start_date`) at which our DAG should be triggered

> The DAG [X] starts being scheduled from the `start_date` and will be triggered after every `schedule_interval`

<img src="/files/images/img22.png" height="55%" width="55%" />


`execution_date` is:

- NOT the date when the DAG has been run
- corresponds to the begining of the processed period (`start_date` - `schedule_interval`)

> IMPORTANT : A DAG with a `start_date` at 10AM and a `schedule_interval` of 10 minutes, gets really executed at 10:10 for data coming from 10AM.

As a best practice, set the `start_date` globally at the DAG level (through `default_args` using datetime object such as `datetime.datetime(2022,9,1)` with (yyyy,m,d) format) and don't use dynamic values such as `datetime.now()`. We can define the `schedule_interval` either with cron expressions (ex: `0 * * * *`) or timedelta objects (ex : `datetime.timedelta(days=1)`) but for a best practice we should use cron expressions rather than timedelta objects.

<img src="/files/images/img23.png" height="55%" width="55%" />

<br><br><br>


## 2. Backfill and Catchup

Sometimes it will happen that our DAG fall in trouble for example a task can fail and so we have to take time in order to fix the issue that basically stop the scheduling the DAG and start debugging, during that time our DAG won't be triggered and it will start accumulating delay.

```bash
airflow backfill -s <start date yyyy-mm-dd> -e <end date yyyy-mm-dd> --rerun_failed_tasks -B <DAG name>
```

The command above is used to run backfill process manually through Airflow CLI and each state describe as below:

- `-s` and `-e` specify repectively the start date and the end date of the date interval we want to backfill
- `--rerun_failed_tasks` allows us to auto-rerun all the failed tasks for the backfill date interval instead of throwing exceptions
- `-B` will force the backfill to run tasks starting from the recent days in first
<br><br><br>


## 3. Dealing with Timezones

There are 2 types of timezone in Python

- Python `datetime.datetime` objects with the tzinfo attribute set
    - Datetime **aware**
    - This happens when we create a datetime object with the timezone defined
    - as a best practice, we should use this type of datetime
        - `datetime.datetime()` in Python gives naive datetime objects by default!!
        - a datetime without a timezone is not in UTC
        - import `airflow.timezone` to create our aware datetime objects or let Airflow does the conversion for us
            - Airflow supports timezones
            - datetime information stored in UTC
            - user interface always shows in datetime in UTC
            - the timezone is set in *airflow.cfg* to UTC by default (`default_timezone = utc`)
            - Airflow uses the pendulum Python library to deal with timezones and the code to supply a timezone aware `start_date` using Pendulum as below
            - ```python
              import pendulum

              local_tz = pendulum.timezone("Europe/Amsterdam")
              # datetime(yyyy,m,d,h)
              default_args = {
                                'start_date' : datetime(2022,3,29,1, tzinfo=local_tz),
                                'owner' : 'Airflow'
                            }

              with DAG('my_dag', default_args=default_args) as dag:
                  .....
              ```
- Python `datetime.datetime` objects with the tzinfo attribute set
    - Datetime **naive**
    - This happens when we create a datetime object without giving the timezone
    - When we use this one, Python will assume that the datetime is already in the default timezone
<br><br><br>


## 4. Tasks Dependent

- `depends_on_past`
    - this is defined at task level
    - if previous task instance failed, the current task is not executed
    - consequently, the current task has no status
    - first task instance with `start_date` allowed to run
    - <img src="/files/images/img24.png" height="60%" width="60%" />
    - ```python
       from airflow import DAG
       from airflow.operators.bash_operator import BashOperator
       from airflow.operators.python_operator import PythonOperator
       from airflow.operators.dummy_operator import DummyOperator
       from datetime import datetime, timedelta

       default_args = {'start_date': datetime(2019, 1, 1),'owner': 'Airflow'}

       def second_task():
           print('Hello from second_task')
           raise ValueError('This will turns the python task in failed state')

       def third_task():
           print('Hello from third_task')
           #raise ValueError('This will turns the python task in failed state')

       with DAG(dag_id='depends_task', schedule_interval="0 0 * * *", default_args=default_args) as dag:
           bash_task_1 = BashOperator(task_id='bash_task_1', bash_command="echo 'first task'")
           python_task_2 = PythonOperator(task_id='python_task_2', python_callable=second_task, depends_on_past=True)
           python_task_3 = PythonOperator(task_id='python_task_3', python_callable=third_task)

           bash_task_1 >> python_task_2 >> python_task_3
      ```
- `wait_for_downstream`
    - this is defined at task level
    - an instance of task X will wait for tasks immediately downstream of the previous instance of task X to finish successfully before it runs
    - <img src="/files/images/img25.png" height="60%" width="60%" />
    - ```python
       from airflow import DAG
       from airflow.operators.bash_operator import BashOperator
       from airflow.operators.python_operator import PythonOperator
       from airflow.operators.dummy_operator import DummyOperator
       from datetime import datetime, timedelta

       default_args = {'start_date': datetime(2019, 1, 1),'owner': 'Airflow'}

       def second_task():
           print('Hello from second_task')
           #raise ValueError('This will turns the python task in failed state')

       def third_task():
           print('Hello from third_task')
           #raise ValueError('This will turns the python task in failed state')

       with DAG(dag_id='depends_task', schedule_interval="0 0 * * *", default_args=default_args) as dag:
           bash_task_1 = BashOperator(task_id='bash_task_1', bash_command="echo 'first task'", wait_for_downstream=True)
           python_task_2 = PythonOperator(task_id='python_task_2', python_callable=second_task)
           python_task_3 = PythonOperator(task_id='python_task_3', python_callable=third_task)

           bash_task_1 >> python_task_2 >> python_task_3
      ```

<br><br><br>


## 5. Deal with Failures

There are 2 levels of failure detection in Airflow:

- DAG failure detections
    - `dagrun_timeout`
        - ```python
          with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, catchup=True, dagrun_timeout=timedelta(seconds=25)) as dag:
          ```
        - this parameter specifies how long a DAGrun should be up before timing out so that new DAGruns can be created
        - this timeout is only effective for scheduled DAGruns so it won't work if we manually trigger our DAG and only once the number of active DAGruns equals to the `max_active_runs_per_dag` parameter
            - `max_active_runs_per_dag` parameter is a configuration property allowing us to fix the max number of active DAGruns per DAG
    - `sla_miss_callback`
        - this parameter allows to call a function when reporting SLA timeouts
    - `on_failure_callback`
        - this parameter is used to call a function when the DAGrun of a DAG fails
        - ```python
          def on_failure_dag(dict):
              print("on_failure_dag")
              print(dict)

          with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, catchup=True, on_failure_callback=on_failure_dag) as dag:
              ...
          ```
    - `on_success_callback`
        - this parameter is used to call a function when the DAGrun of a DAG succeeds
        - ```python
          def on_success_dag(dict):
              print("on_success_dag")
              print(dict)

          with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, catchup=True, on_success_callback=on_success_dag) as dag:
              ...
          ```
- Task failure detections
    - `email`
        - this parameter needs to be defined if we set the `email_on_failure` and `email_on_retry` the parameters equal to True
        - ```python
          default_args = {
              'start_date' : datetime(2021,1,1),
              'owner' : 'airflow',
              'email' : ['youremail@whatemail.com']
          }
          ```
    - `email_on_failure`
        - this parameter will allow Airflow to send an email if there is a task error on our DAGruns
        - ```python
          default_args = {
              'start_date' : datetime(2021,1,1),
              'owner' : 'airflow',
              'email' : ['youremail@whatemail.com'],
              'email_on_failure' : True
          }
          ```
    - `email_on_retry`
        - this parameter will allow Airflow to send an email if a task on DAGruns on the retry process
        - ```python
          default_args = {
              'start_date' : datetime(2021,1,1),
              'owner' : 'airflow',
              'email' : ['youremail@whatemail.com'],
              'email_on_retry' : True
          }
          ```
    - `retries`
        - this parameter indicates the number of retries that should be performed before marking the task as failed
    - `retry_delay`
        - this parameter specifies the delay with a `timedelta` object between retries
        - ```python
          default_args = {
              'start_date' : datetime(2021,1,1),
              'owner' : 'airflow',
              'retries' : 3,
              'retries_delay' : timedelta(seconds=60)
          }
          ```
    - `retry_exponential_backoff`
        - when this parameter is set to True, allows progressive longer waits between retries
    - `max_retry_delay`
        - this parameter defines the max delay interval between retries using a `timedelta` object
    - `execution_timeout`
        - this parameter corresponding to the max allowed execution time of a given task instance, expressed with a `timedelta` object
        - if a task takes more than `execution_timeout` to finish, it's marked as failed
    - `on_failure_callback`
        - this parameter is used to call a function when the task of a DAGrun fails
        - ```python
          def on_failure_task(dict):
              print("on_failure_task")
              print(dict)

          default_args = {
              'start_date' : datetime(2021,1,1),
              'owner' : 'airflow',
              'on_failure_callback' : on_failure_task
          }
          ```
    - `on_success_callback`
        - this parameter is used to call a function when the task of a DAGrun succeeds
        - ```python
          def on_success_task(dict):
              print("on_success_task")
              print(dict)

          default_args = {
              'start_date' : datetime(2021,1,1),
              'owner' : 'airflow',
              'on_success_callback' : on_success_task
          }
          ```
    - `on_retry_callback`
        - this parameter is used to call a function when the task of a DAGrun retries
<br><br><br>


## 6. Unit Testing

It's crucial to make unit tests in order to be sure that nothing gets broken after our application has been modified and it's even more important as we can work with different teams.


[Pytest](https://docs.pytest.org/en/latest) is one of Python testing tools that can be used for unit testing which is a testing framework which allows us to write very simple test codes as well as complex functional testing for applications and libraries and it's widely used by the community. With [Pytest](https://docs.pytest.org/en/latest), the things that we can test in Airflow are:

- DAG Validation Tests
    - check if valid, this will verify if there are any typos in our DAG
    - check if there is no cycles
    - check default arguments aer correctly set
- DAG Definition Tests
    - check total number of tasks
    - check the nature of tasks
    - check the upstream and downstream dependencies of tasks
- Unit Tests
    - unit testing external functions or custom operators
    - check the logic
- Integration Tests (tests if tasks work well with each others using a subset of production data)
    - check if tasks can exchange data
    - check the input of tasks
    - check dependencies between multiple tasks
    - these tests can be complex and slower than other tests as we gonna need to deal with external tools such as Spark, PostgreSQL, or etc
    - we'll need to set up a different environment (development/test/acceptance/production environments)
- End-to-end Pipeline Tests (test the data pipeline)
    - check the full logic of our DAGs from the first task to the last one
    - check if the output is correct
    - check the performance
    - we'll need to set up a different environment (development/test/acceptance/production environments)

> The example of DAG Validation Tests and DAG Definition Tests can be found under *dag_validation_and_definition_tests* folder and to run the test we can just run the *test_dag_validation.py* file for DAG Validation Tests and *test_tst_dag_definition.py* file for DAG Definition Tests through CLI and don't forget to put `-v` (ex : `pytest test_dag_validation.py -v`) in the command to activate the verbose.

<img src="/files/images/img26.png" height="55%" width="55%" />

<img src="/files/images/img27.png" height="55%" width="55%" />