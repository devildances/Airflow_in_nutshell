'''
The BaseOperator is a very important class, whenever we create a new operator then we have to make sure that it
inherits from the BaseOperator class. This is used by all operators in order to be sure that they all share the
same minimum functions and attributes.
'''
from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from elasticsearch_plugin.hooks.elastic_hook import ElasticHook

from contextlib import closing
import json

class PostgresToElasticOperator(BaseOperator):

    # ==================================== OVERRIDE INIT METHOD ====================================
    '''
    we've to override the init method in order to  initialize our operator
    - sql : it would be executed by the Hook to fetch the data that we want to trf to ElasticSearch
    - index : the index of ElasticSearch where the data will be stored
    - postgres_conn_id : it's corresponding to the connection of postgres
    - elastic_conn_id : it's corresponding to the connection of ElasticSearch
    - 
    '''
    def __init__(self, sql, index, postgres_conn_id="postgres_default", elastic_conn_id="elasticsearch_default", *args, **kwargs):
        super(PostgresToElasticOperator, self).__init__(*args, **kwargs)

        self.sql = sql
        self.index = index
        self.postgres_conn_id = postgres_conn_id
        self.elastic_conn_id = elastic_conn_id
    # ==================================== END OF OVERRIDE INIT METHOD ====================================

    # ==================================== OVERWRITE EXECUTE METHOD ====================================
    '''
    when we create a new Operator in Airflow, we absolutely
    have to overwrite one method which is execute. This method
    is where we implement the task that we want to achieve with
    our Operator and that method will be triggered by the executor
    '''
    def execute(self, context):
        '''
        so here we've to put the logic in order to transfer data
        from postgres to ElasticSearch
        '''

        # first, instantiate the Hook and the ElasticHook
        es = ElasticHook(conn_id=self.elastic_conn_id)
        pg = PostgresHook(postgres_conn_id=self.postgres_conn_id)

        # second, get the connection from postgres
        with closing(pg.get_conn()) as conn:
            '''
            by doing this, we create a connection using the PostgresHook and
            we automatically close it as soon as we don't need it anymore
            with closing
            '''

            # get the cursor
            with closing(conn.cursor()) as cur:
                '''
                the cursor can be used as a way to interact with postgres and
                in this case we're going to use it in order to execute SQL requests
                '''

                # as we can have GB to transfer, we can define the number of rows that we want to fetch at a time
                cur.itersize = 1000

                # then we execute the SQL request
                cur.execute(self.sql)

                for row in cur:
                    # for each row we create the corresponding JSON as the document so we can add it into ElasticSearch
                    doc = json.dumps(row, indent=2)
                    es.add_doc(index=self.index, doc_type="external", doc=doc)

    # ==================================== END OF OVERWRITE EXECUTE METHOD ====================================