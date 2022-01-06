from airflow import DAG
from airflow.operators.bash import BashOperator

from datetime import datetime

default_args = {
    "start_date" : datetime(2021,12,5)
}

with DAG(dag_id="trigger_rule", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    task_1 = BashOperator(
        task_id = 'task_1',
        bash_command = 'exit 1', # 0 means successfully exit, and 1 is the opposite
        do_xcom_push = False # this paramater is to set if we want to send the XCom value or not into our meta database
    )

    task_2 = BashOperator(
        task_id = 'task_2',
        bash_command = 'exit 1', # 0 means successfully exit, and 1 is the opposite
        do_xcom_push = False # this paramater is to set if we want to send the XCom value or not into our meta database
    )

    task_3 = BashOperator(
        task_id = 'task_3',
        bash_command = 'exit 0', # 0 means successfully exit, and 1 is the opposite
        do_xcom_push = False, # this paramater is to set if we want to send the XCom value or not into our meta database
        trigger_rule = 'all_failed'
    )

    task_4 = BashOperator(
        task_id = 'task_4',
        bash_command = 'exit 1', # 0 means successfully exit, and 1 is the opposite
        do_xcom_push = False # this paramater is to set if we want to send the XCom value or not into our meta database
    )

    task_5 = BashOperator(
        task_id = 'task_5',
        bash_command = 'exit 0', # 0 means successfully exit, and 1 is the opposite
        do_xcom_push = False # this paramater is to set if we want to send the XCom value or not into our meta database
    )

    task_6 = BashOperator(
        task_id = 'task_6',
        bash_command = 'exit 0', # 0 means successfully exit, and 1 is the opposite
        do_xcom_push = False, # this paramater is to set if we want to send the XCom value or not into our meta database
        trigger_rule = 'all_done'
    )

    [task_1, task_2] >> task_3
    [task_4, task_5] >> task_6