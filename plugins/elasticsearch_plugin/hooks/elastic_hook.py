from airflow.hooks.base import BaseHook
from elasticsearch import Elasticsearch

class ElasticHook(BaseHook):

    # overwrite the init method
    def __init__(self, conn_id='elasticsearch_default', *args, **kwargs):
        # by default the Hook will use the connection ID elasticsearch_default that we'll have to create from the UI of Airflow

        # ================================ CREATE ALL THE ATTRIBUTES OF THE CONNECTION ================================
        super().__init__(*args, **kwargs)
        '''
        once we've created the connection from the UI of Airflow we need to fetch it from 
        our Hook using get_connection which is a method coming from BaseHook
        '''
        conn = self.get_connection(conn_id)

        # get the attributes of that connection
        conn_config = {}
        hosts = []

        if conn.host:
            # we split using coma means if there is multiple hosts separated with a comma then we want to create a list 
            hosts = conn.host.split(',')

        if conn.port:
            # if there's a port then we want to make sure that it's an integer not float
            conn['port'] = int(conn.port)

        if conn.login:
            # if there is a login, then we want to added in conn_config
            # this is not required, that's why we're not checking the password
            conn_config['http_auth'] = (conn.login, conn.password)
        # ================================ END OF CREATE ALL THE ATTRIBUTES OF THE CONNECTION ================================

        # ==================================== CREATE ELASTICSEARCH OBJECT ====================================
        self.es = Elasticsearch(hosts, **conn_config)

        # as ElasticSearch stores data in indexes, we can specify it
        self.index = conn.schema
        # ==================================== END OF CREATE ELASTICSEARCH OBJECT ====================================

    # ==================================== CREATE SOME ADDITIONAL METHODS ====================================
    def info(self):
        # this method is used to get some information about our ElasticSearch instance
        return self.es.info()

    def set_index(self, index):
        # this method is used if we want to define an index
        self.index = index

    def add_doc(self, index, doc_type, doc):
        '''
        this method is used to add a document or data in the specific index
        - index param for specify the index where the document will be stored
        - doc_type param can be whatever we want
        - doc param is the document or data that we want to store
        '''
        self.set_index(index)
        res = self.es.index(index=index, doc_type=doc_type, body=doc)
        return res
    # ==================================== END OF CREATE SOME ADDITIONAL METHODS ====================================