from airflow import DAG
from elasticsearch_plugin.hooks.elastic_hook import ElasticHook
from elasticsearch_plugin.operators.postgres_to_elastic import PostgresToElasticOperator #last
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    "start_date" : datetime(2021,12,5)
}

def _print_es_info():
    # second, create this function to instantiate ElasticHook object and print the information of our ElasticSearch instance
    hook = ElasticHook()
    print(hook.info())

with DAG(dag_id='elasticsearch_dag', schedule_interval='@daily', default_args=default_args, catchup=False) as dag:

    # first, we add an operator (Python operator) in order to use our Hook
    print_es_info = PythonOperator(
        task_id = 'print_es_info',
        python_callable = _print_es_info
    )

    connections_to_es = PostgresToElasticOperator(
        task_id = 'connections_to_es',
        sql = 'SELECT * FROM connection',
        index = 'connections'
    ) #last

    print_es_info >> connections_to_es