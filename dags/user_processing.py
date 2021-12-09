from airflow.models import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator

# we don't use providers to import PythonOperator and BashOperator because they brought by default with Airflow
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime
import json, pandas as pd

default_args = {
    'start_date' : datetime(2021,12,5)
}

def _processing_user(ti):
    # xcom_pull can be used to fetch the results from the previous task by given task ID
    users = ti.xcom_pull(task_ids=['extracting_user'])

    if not len(users) or 'results' not in users[0]:
        raise ValueError('User is empty')

    user = users[0]['results'][0]
    processed_user = pd.json_normalize({
        'firstname' : user['name']['first'],
        'lastname' : user['name']['last'],
        'country' : user['location']['country'],
        'username' : user['login']['username'],
        'password' : user['login']['password'],
        'email' : user['email']
    })

    # store the data into our tmp folder for temporary, because that data will be used in next task
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)

# instantiate the DAG and also all the parameters
with DAG('user_processing', schedule_interval='@daily',
        default_args=default_args, catchup=False) as dag:
    # Define the tasks/operators
    '''
    in this example, we will create 5 tasks:
    1. creating_table
        - this task allows us to create a table in SQLite DB
        - for this task, we'll use the SQLite Operator
    2. is_api_available
        - as we want to be sure that the API where we're going to fetch the users is available
        - in this task we're going to use the HTTP Sensor, it waits for something to happen before moving to the next task
    3. extracting_user
        - from this task, we're going to fetch the user from the API
        - the operator that we could use in order to fetch the result from the API is HTTP operator
        - SimpleHttpOperator allows us to fetch the result of a given URL
    4. processing_user
        - from extracting_user task, we got many different information and actually what we would like is to get only
          the information that we are going to store in the table
        - in this task, we're going to use the Python operator to get only some of field we need
    5. storing_user
        - for this task, we'll use BashOperator
    '''

    creating_table = SqliteOperator(
        task_id = 'creating_table', # this task_id must be unique among all of our tasks inside the same data pipeline
        sqlite_conn_id = 'db_sqlite', # a connection to interract with the SQLite DB
        sql = '''
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL PRIMARY KEY
            );
            '''
    )

    is_api_available = HttpSensor(
        task_id = 'is_api_available',
        http_conn_id = 'user_api',
        endpoint = 'api/'
    )

    extracting_user = SimpleHttpOperator(
        task_id = 'extracting_user',
        http_conn_id = 'user_api',
        endpoint = 'api/',
        method = 'GET',
        response_filter = lambda response: json.loads(response.text),
        log_response = True
    )

    processing_user = PythonOperator(
        task_id = 'processing_user',
        python_callable = _processing_user # in this parameter, we pass python function
    )

    storing_user = BashOperator(
        task_id = 'storing_user',
        bash_command = 'echo -e ".separator ","\n.import /tmp/processed_user.csv users" | sqlite3 /home/airflow/airflow/airflow.db'
    )


    # Here we define our dependencies in this DAG
    creating_table >> is_api_available >> extracting_user >> processing_user >> storing_user