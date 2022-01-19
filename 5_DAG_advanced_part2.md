## 7. Branching

Branching is the way to go down a certain path in our DAG based on an arbitrary condition which is typically related to something that happened in an upstream task. This is done by using the `BranchPythonOperator` that returns the `task_id` of the task to execute next.

<img src="/files/images/img28.png" height="55%" width="55%" />

For example, we've the DAG above with 3 tasks depending on the task implemented with the `BranchPytonOperator`. Let's say that the task return the value of the `task_id` is `task_c` therefore only task_c will be executed whereas task_a and task_b will be skipped.

> The example code of branching can be found in the *branch_condition.py* file under *dags* folder.

<br><br><br>


## 8. Trigger Rules

<img src="/files/images/img29.png" height="55%" width="55%" />

> The example code of Trigger Rules can be found in the *trigger_rule_dag.py* file under *dags* folder.

<br><br><br>


## 9. Avoid Hard Coding Values (Variables, Templates and Macros)

### 9.a Variables

- A variable is nothing more than an object, a value stored into the metadata database of Airflow
- There are 2 ways of creating variables, either from the CLI or UI
- A variable is composed by a key and a value with 3 columns
    - Key
    - Value
    - Is encrypted
        - Notice that we can encrypt our variables only if the package Crypto is installed along with our instance of Airflow
- It's absolutely possible to push JSON object as the value of a variable


Key | Value | Is encrypted
--- | --- | ---
my_settings | {login:"me", pass:"secret"} | Yes

<br><br>

### 9.b Templating

<img src="/files/images/img30.png" height="55%" width="55%" />

- Replace placeholders by values at runtime
    - templating allows us to interpolate values at run time in static files such as HTML or SQL files by placing special placeholders in them indicating where the values should be and how they should be displayed
    - think of templating as a way of filling in blanks in our code by external values
- Based on Jinja Templating
    - templating in Airflow is based on Jinja which is a template engine for Python in charge of replacing the placeholders with the expected values and more
- Placeholders : {{}}
    - in Airflow to indicate a placeholder we use 2 pairs of curly brackets
    - those curly bracketsindicate to Jinja that there is something to interpolate in there
- Can be used with template parameters
- Templating is a really powerful concepts as we can insert data at runtime without knowing the value in advance and so it makes our code even more dynamic
<br><br>


### 9.c Macros

<img src="/files/images/img31.png" height="55%" width="55%" />

- Macros are functions that are predefined by Airflow
- Actually Airflow brings us both predefined Macros and Variables that we can use within our templates as per image above
    - They are very useful since they allow us to get the information about the current executing DAG or task
<br><br>

> The example code of Variables, Templates and Macros can be found in the *template_dag.py* file under *dags* folder.

<br><br><br>


## 10. XCOM

XCOM stands for *cross-communication* allowing for our tasks to exchange data and states between them where can be a great help as we get more control on our tasks but can also be dangerous as we may fall down to the temptation of taking AIrflow for a data streaming solution.

<img src="/files/images/img32.png" height="50%" width="50%" />

XCOMs are defined by a key, a value and a timestamp. The key is defined as a simple string where the value can be any object that can be pickled.

> Best practice : XCOMs don't have a limit in size but we should keep them very lightweight or we may risk to slow down our data pipeline and even make our Airflow instance unstable so don't ever think of sharing a dataframe of million or rows between our tasks. Otherwise use an external system like a database to share intermediate data.

The `task_id` of the task having pushed the XCOM is filled as well as the `dag_id` from which it comes from. This allows us to retrieve an XCOM by using the task ID or limiting the search for an XCOM to a specific DAG ID.


<img src="/files/images/img33.png" height="55%" width="55%" />

There are 2 ways to push an XCOM into metadata database in order to share data between 2 operators:

- First way, we can call the method `xcom_push`
    - this method expects a key and a value
- Or second way, by returning a value from the execute method of an Operator or from the Python callable function of the PythonOperator
    - in this case, only the value will be returned and the key will automatically assigned to the string `"return_value"`


Once the XCOM is stored into the metadata database, the 2nd operator can pull that value by calling the method `xcom_pull`. There are different ways of pulling XCOMs values:

- First, we can specify the key of the `xcom_push` we want and it becomes available in our operator
- Another way, is to specify only the task ID of the task having pushed the COM we want
    - for example, let's say task 1 has pushed an XCOM then in task 2 we can call the method `xcom_pull` with the `task_ids=["Task1"]` and we will obtain the most recent XCOM pushed by the task 1 so that's why a timestamp exists along with XCOMs to order them from the most recent one to the oldest


NOTES : One thing we must keep in mind is that AIrflow won't automatically clean our XCOMs, it's up to us to do the job and create an automatic process to clean all of those, otherwise at some point we'll waste space resources of our metadata database.

> The example code of XCOMs can be found in the *xcom_a_dag.py*, *xcom_b_dag.py* and *xcom_big_dag.py* files under *dags* folder.

<br><br><br>


## 11. TriggerDagRunOperator

`TriggerDagRunOperator` allows us to trigger another DAG from a DAG or more specifically it triggers a DAGrun for a specified DAG ID when a condition is met.

<img src="/files/images/img34.png" height="50%" width="50%" />

For example, we have a DAG which is the controller and another DAG which is the target. From the controller we need to instantiate a task with the `TriggerDagRunOperator`. This operator expects multiple arguments such as:

- `trigger_dag_id`
    - this is corresponding to the DAG we want to trigger
- `python_callable`
    - function where the condition will be checked if the target DAG can be trigger or not
- `params`
    - and some parameters that we'll be able to send from the controller to the target DAG


Important notes:

- Controller doesn't wait for target to finish
- Controller and target are independent
- No visualization from the controller neither history
- Both DAGs must be scheduled
- Target DAG schedule interval equals to None


> The example code of `TriggerDagRunOperator` can be found in the *triggerdagop_controller_dag.py* and *triggerdagop_target_dag.py* files under *dags* folder.

<br><br><br>


## 12. ExternalTaskSensor for dependencies between our DAGs

Sensor is a special kind of operators witing for something to happen and that's exactly what the `ExternalTaskSensor` does but this time it waits for an external task to finish before moving to the next task and that's how we can create dependencies between our DAGs. Imagine that we have 2 DAGs where the first one extracts data from production databases and the second one aggregates the data to push the result into another database then the thing we can do is to wait for the first DAG to finish before starting the second DAG by implementing `ExternalTaskSensor` we can postpone the start of the second DAG until the first one successfully finishes.

<img src="/files/images/img35.png" height="50%" width="50%" />

As per image above, we have `DAG 1` and `DAG 2`. Both DAGs have the same `schedule_interval` because the `ExternalTaskSensor` assumes that both DAGs are the same execution date. If our DAGs don't have the same execution date but still have the same `schedule_interval` we can still use the sensor by modifying the parameters `execution_delta` or `execution_date_fn` so both DAGs have the same `schedule_interval`. In the example `DAG 2` will wait for the last task of `DAG 1` which is `t3` before moving to thext task by using the `ExternalTaskSensor` as first task waiting for the task `t3` of `DAG 1` ro succeed.


Important notes:

- We should keep the same `schedule_interval` between our dependent DAGs
- If we use this sensor and our DAGs don't have the same `execution_date` the we can solve this by defining either `execution_delta` or `execution_date_fn` parameters and **NEVER BOTH**
    - `execution_delta` is the time difference with the previous execution to look at and the default is the same execution date as the current task
        - for example if we have 2 DAGs running every hour but the first DAG is triggered at 10:00AM and the second DAG at 10:30AM then we just need to assign a `timedelta(minutes=30)` to the parameter `execution_delta`
        - by doing so, the execution dates will be the same for the `ExternalTaskSensor`
    - `execution_date_fn` follows the same purpose of `execution_delta` but in a more flexible way
        - this parameter expects a function that receives the current execution date and returns the desired execution date
- By default the sensor will use the *poke* method to check if the task from the other DAG succeed or not
    - we should use the *reschedule* mode if needed which is considered as a best practice with the `ExternalTaskSensor` to avoid wasting worker slots


> The example code of `ExternalTaskSensor` can be found in the *externaltasksensor_dag.py* and *sleep_dag.py* files under *dags* folder.