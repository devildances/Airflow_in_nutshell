from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup

from random import uniform
from datetime import datetime

default_args = {
    "start_date" : datetime(2021,12,5)
}

def _training_model(ti):
    accuracy = uniform(0.1, 10.0)
    print(f"model's accuracy: {accuracy}")

    # this is how we push the value of XCom into our meta database
    ti.xcom_push(key='model_accuracy', value=accuracy)

def _choose_best_model(ti):
    print("choose best model")

    # this is how we pull the values of XCom from our meta database
    accuracies = ti.xcom_pull(key = 'model_accuracy',
                            task_ids= [
                                'training_model_a',
                                'training_model_b',
                                'training_model_c'
                            ])

    for accuracy in accuracies:
        if accuracy > 5:
            # this means the next task that we want to execute should've the task_id = 'accurate'
            return 'accurate'

    # this means the next task that we want to execute should've the task_id = 'inaccurate'
    return 'inaccurate'

    '''
    If we want to return multiple task IDs we can do that by using this format code
    return ['task_id_1', 'task_id_2', ..., 'task_id_n']
    '''

with DAG(dag_id="xcom_dag", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:

    downloading_data = BashOperator(
        task_id = 'downloading_data',
        bash_command = 'sleep 3',
        do_xcom_push = False # this paramater is to set if we want to send the XCom value or not into our meta database
    )

    with TaskGroup('processing_tasks') as processing_tasks:
        training_model_a = PythonOperator(
            task_id = 'training_model_a',
            python_callable = _training_model
        )

        training_model_b = PythonOperator(
            task_id = 'training_model_b',
            python_callable = _training_model
        )

        training_model_c = PythonOperator(
            task_id = 'training_model_c',
            python_callable = _training_model
        )

    choose_model = BranchPythonOperator(
        task_id='choose_best_model',
        python_callable=_choose_best_model
    )

    accurate = DummyOperator(
        task_id = 'accurate'
    )

    inaccurate = DummyOperator(
        task_id = 'inaccurate'
    )

    storing = DummyOperator(
        task_id = 'storing'
    )

    downloading_data >> processing_tasks >> choose_model
    choose_model >> [accurate, inaccurate] >> storing