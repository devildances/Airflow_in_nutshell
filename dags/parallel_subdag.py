from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator

from subdags.subdag_parallel_dag import subdag_parallel_dag

from datetime import datetime

default_args = {
    "start_date" : datetime(2021,12,5)
}

with DAG(dag_id='parallel_subdag', schedule_interval='@daily', default_args=default_args, catchup=False) as dag:

    task_1 = BashOperator(
        task_id = 'task_1',
        bash_command = 'sleep 3'
    )

    processing = SubDagOperator(
        task_id = 'processing_tasks',
        subdag = subdag_parallel_dag('parallel_subdag', 'processing_tasks', default_args)
    )

    task_4 = BashOperator(
        task_id = 'task_4',
        bash_command = 'sleep 3'
    )

    # parallel DAGs for task_2 and task_3 in processing
    task_1 >> processing >> task_4