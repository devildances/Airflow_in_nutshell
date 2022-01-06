# Create Airflow Plugins with ElastichSearch and PostgreSQL

At this point, we'll answer some important questions:

- How to extend features and functionalities?
    - Airflow allows us to customize it as much as we need in order to get an Airflow instance that fits with our needs
- How the plugin system works?
    - It's super important to know what we can do, what we can't do and how can we do it well
- How to create our own operator?
    - we'll create an Operator, a View and a custom Hook
        - Hook allows us to interact with an external tool



## Installing ElasticSearch

Elasticsearch is search engine providing a way of searching in data at scale in a very efficient way. In a nutshell, we have a lot of logs to analyse, Elasticsearch does a very good job at analysing them.

First, as we want to interact with Elasticsearch from Airflow, we need to install it in our virtual machine

- Open a terminal to install it
    - execute `curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -` command
        - input `airflow` as the password
    - then execute `echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list` command
    - and next execute `sudo apt update && sudo apt install elasticsearch` command
    - activate python3 virtual environment then install ElasticSearch package by running `pip install elasticsearch==7.10.1` command
- Open new terminal to start and test ElasticSearch that already installed
    - start it by executing `sudo systemctl start elasticsearch` command
    - Check if ElasticSearch works with `curl -X GET 'http://localhost:9200'` command



## The Plugin System

Airflow is not only powerful because we can code our data pipelines using python but also because we can extend its functionalities and features so that at the end we'll get an Airflow instance fitting with our needs.


Things that we can customize in Airflow are:

- Operators
    - we can create our own operators
    - for example we have postgres operator but that operator doesn't allow us to fetch data from database (we can execute SQL requests but we can't get results from the database)
        - to fix this, we can create our own operator extending the functionalities of the postgres operator
        - so either we create operator that extending functionalities of existing operators or we can create our own operator
- Views
    - if we have some tools with which we are interacting with from our data pipelines and we would like to monitor from our Airflow instance which one is on and which one is off then we could definitely do that by adding a new View in our Airflow instance
    - we can customize the UI of Airflow as much as we need
        - we can add new pages, add new menu links and so on
- Hooks
    - when a new tool came out and we want to interact with that new tool then the answer is using Hook in order to interact with a third party tool
    - we can create our own Hook in Airflow


To add Plugins in Airflow we can do the following:

- First, we have to know that by default there are 3 folders that Airflow monitors for us (the folder plugins, coffee and dags)
- We'll put our files corresponding to our Plugins inside the folder plugins
    - this folder is not automatically created so we have to create it by ourselves
    - historycally, before Apache Airflow 2.0, we had to use the *AirflowPluginClass* and more specifically we had to create a class corresponding to our Plugin inheriting from *AirflowPluginClass*
        - before Apache Airflow 2.0 we had to specify our operators, hooks, executors, views and so on inside that class
        - but this is not the case anymore in Apache Airflow 2.0
        - in Apache Airflow 2.0 the *AirflowPluginClass* is only used for customizing the UI of Airflow
        - otherwise we just need to create **Regular Python Modules**
    - inside the plugins folder we create a new folder with the name of our Plugin then we put the files corresponding to our Plugin and then we'll be able to import it directly from our data pipelines


These are how we load our Plugins in Airflow:

- By default Plugins are *Lazy Loaded* which means whenever we add a new plugin in our Airflow instance we have to restart it otherwise it won't work because Airflow won't be aware of our new plugin
- Once we've added our plugin we can definitely modify it without having to restart our Airflow instance again and again



## Start build the connection!!

Now we'll create a plugin that interact with ElasticSearch and more specifically we're going to create 2 things:

- Hook
    - this is used to interact with ElasticSearch
    - as we want to add a plugin into Airflow we need to create a folder *plugins*
        - inside this folder we create a new folder named *elasticsearch_plugin*
            - and inside it we create a new folder called *hooks*
                - this is where we're going to put the file corresponding to our Hook
                - create new file called *elastic_hook.py*
                    - we have to import `BaseHook` module
                        - ```python
                          from airflow.hooks.base import BaseHook
                          ```
                        - this class is used by all Hooks in order to share some minimum attributes and methods
                        - also, whenever a class inheretis from BaseHook that indicates to Airflow that this class is a Hook
                    - import the ElasticSearch object in order to interact with it
                        - ```python
                          from elasticsearch import ElasticSearch
                          ```
                    - and now we're ready to implement the class corresponding to our Hook
                        - the code attached on the folder
                    - next is activating our Airflow and make sure to enable our python virtual environment
                        - run `airflow webserver` and `airflow scheduler` commands
                        - check on the webserver terminal and verify that we don't have any errors right there
                    - now let's try the Hook within the DAG
    - create new DAG to use our new Hook in *dags* folder
        - create new DAG file under this folder called *elasticsearch_dag.py*
            - on this file we create a DAG as usual
    - test our new DAG from Airflow UI (localhost:8080)
        - check the log of our task in that DAG
        - it will show the information of our ElasticSearch instance
    - at this point we've successfully built a Hook and we've successfully added that Hook in our Airflow instance
        - whenever we have a new tool and we want to interact with it then create our own Hook
- Custom Operator
    - for this, we'll create a custom Operator in order to transfer data from PostgreSQL to ElasticSearch using the Hook that we built
    - create new folder under *plugins/elasticsearch_plugin* called *operators*
        - inside this folder we create a new file named *postgres_to_elastic.py*
            - in this file we create our custom Operator
    - at this point we've successfully created an Operator in order to trasfer data from postgres using the PostgresHook to ElasticSearch using our ElasticHook


So let's verify if it works.

- first we need to create the postgres connection
    - go to the Airflow UI
    - click *Admin* on the menu bar and click *Connections* option
    - look for `postgres_default`, if we obtain it then delete it and then create it again with these values:
        - Conn id : `postgres_default`
        - Conn Type : `Postgres`
        - Host : `localhost`
        - Login : `postgres`
        - Password : `postgres`
        - Port : `5432`
        - Extra : `{"cursor":"realdictcursor"}`
            - on this field, we've to specify the cursor that we want to use
            - this part is really importan because by using that cursor we'll be able to transform the rows in JSON
    - click on *Save* button in order to create the connection
- then we need to create a password for postgres, we put the password value on the above but we didn't create it yet
    - go back to the terminal
    - run `sude -u postgres psql` command
        - input `airflow` if it asks for password
    - we'll be inside the postgres interpreter
        - run `ALTER USER postgres PASSWORD 'postgres';` command
        - hit ctrl+D to exit
        - now the password has been added for postgres user in order to interact with postgres


For example purpose to transfer data from postgres to ElasticSearch, we're going to transfer the connections that we have in the meta database of Airflow into ElasticSearch. We can check those connections if we run `SELECT * FROM connection;` command on the postgres interpreter.

To check data that we have in ElasticSearch, we can run `curl -X GET "http://localhost:9200/connections/_search" -H "Content-type: application/json" -d '{"query":{"match_all":{}}}'` command from the terminal.


Now we build the code to send the data using the *PostgresToElasticOperator*.

- open the *elasticsearch_dag* file under *dags* folder then modify it and give `#last` for every code that we create to give a sign as we modify it in the final step
- after that we're ready to test if it works
    - open the Airflow UI (localhost:8080)
    - click on *DAGs* on the menu bar and choose `elasticsearch_dag` from the DAG list
    - click on *Graph View*
    - run the DAG by click the trigger button on the top right
    - check the log if any error exists
- go back to the terminal
- check the data that we have in ElasticSearch to make sure that our DAG is running well
    - run `curl -X GET "http://localhost:9200/connections/_search" -H "Content-type: application/json" -d '{"query":{"match_all":{}}}'` command
    - as we can see right there, we have all the connections information from Airflow stored inside ElasticSearch