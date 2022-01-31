# Monitoring Apache Airflow

- Based on the logging module
    - The logging system of Airflow is based on the Python *logging* standard library that offers us a lot of flexibility in terms of configuration
    - As reminder, logs are described as the stream of aggregated, time-ordered events collected from the collected from the output streams of all running processes and backing services
- Written into files
    - Airflow relies on many components such as a web server, a scheduler and one-to-many workers where each component generates its own stream of logs which will be stored into a file by default by using the *logging* module
- Log levels
    - *logging* module allows us to create a logger object which is in charge of obtaining the logs we want according to a defined log level such as INFO, ERROR, DEBUG, WARNING or CRITICAL
    - This level can be found in *airflow.cfg* file with `logging_level` variable
- Formatters
    - The logs is formatted according to the configuration set in the *airflow.cfg* file
- All logs are redirected to a specified destination denending on the Handler used
    - FileHandler
        - this handler writes output to a disk file
        - by default, it is set and the logs are stored at the destination specified in the parameter `base_log_folder` in *airflow.cfg* file
    - StreamHandler
        - this handler writes output to a stream
    - NullHandler
        - this handler does nothing
        - this handler only for testing and developing so actually we should never use it



The code below shows how the logging system is created.

```python
def setup_logging(filename):
    """Creates log file handler for daemon process"""
    root = logging.getLogger()
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter(settings.SIMPLE_LOG_FORMAT)
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(settings.LOGGING_LEVEL)

    return handler.stream
```

- `getLogger()`
    - a logger object is fetched from the logger module
- `FileHandler`
    - instantiate the handler
- `Formatter(settings.SIMPLE_LOG_FORMAT)`
    - instantiate the formatter
    - this parameter can be found in the *airflow.cfg* file and it allows us to specify how to format the output of our logs if we want to add the time, the loglevel and so on
- `setFormatter`
    - the formatter is set to the handler
- `addHandler`
    - the handler is set to the logger object
- `setLevel(settings.LOGGING_LEVEL)`
    - the `LOGGING_LEVEL` is applied to the logger in order to filter the logs accordign to the level set (INFO, ERROR, DEBUG, WARNING or CRITICAL)


<img src="/files/images/img36.png" height="50%" width="50%" />


> Copy the code under https://github.com/apache/airflow/blob/main/airflow/config_templates/airflow_local_settings.py to the local (we can put it on mounting folder of Airflow under conf folder) and add the config dictionary to the `logging_config_class` variable in *airflow.cfg* file with the value of `<filename>.DEFAULT_LOGGING_CONFIG`

<br><br>

## 1. Log Monitoring Architecture

<img src="/files/images/img37.png" height="50%" width="50%" />

The image above is the architecture we're going to set up for writing and reading log events of Airflow in ElasticSearcg by using FileBeat, LogStash, ElasticSearch and Kibana. Basically, we'll have 3 Docker containers corresponding to LogStash, ElasticSearch and Kibana as well as another container where the Airflow worker is running.

- <img src="/files/images/img38.png" height="40%" width="40%" />
    - inside the Airflow worker container we'll install FileBeat in order to fetch the logs and ship them to LogStash
    - IMPORTANT : Airflow won't write the log events directly into ElasticSearch
        - when a DAG will be triggered, the log events of a given task will be stored in JSON into local log files
        - log files will be at the path given by the parameter `based_log_folder` which is `/usr/local/airflow/logs` by default
- <img src="/files/images/img39.png" height="40%" width="40%" />
    - each time a new log file is produced, FileBeat will process it add an offset to each log event and send the output to LogStash
- <img src="/files/images/img40.png" height="45%" width="45%" />
    - LogStash will get the logs and will apply some transformations in order to generate a `log_id` field required by Airflow to finally ship them into ElasticSearch
- <img src="/files/images/img41.png" height="40%" width="40%" />
    - once the data are stored into ElasticSearch, we'll be able to monitor our DAGs through Kibana by making dashboards


There are 2 important points in order to read the logs from ElasticSearch, Airflow assumes 2 things:

- first, our log event should have a field called `offset` which will be used to display the logs in the right order
    - this `offset` is automatically created by FileBeat when a given file is processed
- second, Airflow assumes that a `log_id` field crresponding to the concatenation of the `dag_id`, `task_id`, `execution_date` and `try_number` as `{dag_id}-{task_id}-{execution_date}-{try_number}` is defined for each log event
    - the `log_id` field will be used by Airflow in order to retrieve the log from ElasticSearch
    - this field is not automatically created by LogStash so we have to define some transformations thorugh LogStash in order to generate it

> This project is contained under *logger* folder

<br><br>

## 2. Configure Airflow Configuration File to Work with ElasticSearch

- since we're going to use a remote storage (ElasticSearch) for the logs, we have to set the `remote_logging` parameter to `True`
- look for the `[elasticsearch]` section
    - set the `host` parameter to `http://elasticsearch:9200`
        - since we're using Docker, notice that value corresponds to the service name running ElasticSearch which is `elasticsearch`
    - set the `write_stdout` parameter to empty (`write_stdout=`)
        - this parameter allows us to write the task logs to the standard output of the worker instead of the default files
        - since we actually want to store the logs in the default files then remove the value and let the parameter empty
        - if we keep this parameter sets to `False` with ElasticSearch enabled then the log files won't be produced
    - set the parameter `json_format` to `True`
        - we set the value as `True` since ElasticSearch expects JSON data
- Open new terminal and go to the *logger* folder
    - Start the docker containers by running `docker-compose -f docker-compose-CeleryExecutorELK.yml up -d` command
- Open new browser and go to http://localhost:9200
    - this will show us some information about ElasticSearh
- Open new tab from existing browser and go to http://localhost:5601 to open Kibana UI
- Open new tab from existing browser and go to http://localhost:8080 to open Airflow UI
- Back to our terminal and connect to the Airflow worker by running `docker exec -it <worker container ID> /bin/bash` command
    - at this point, Airflow is configured to read task logs from ElasticSearch
    - now we need to setup FileBeat in order to ship the logs into LogStash to finally store them into ElasticSearch so that we'll be able to read them from the Airflow UI
        - first, we need to download FileBeat by running `curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.5.2-linux-x86_64.tar.gz` command
        - extract the file by running `tar xvzf filebeat-7.5.2-linux-x86_64.tar.gz` command
        - go inside of the filebeat folder
        - open the configuration file of FileBeat by running `[vi | vim] filebeat.yml` command
            - change the input configuration as True `enabled: true`
            - change the Glob based paths where the logs file are as `/usr/local/airflow/logs/*/*/*/*.log`
                - each wildcard (`*`) corresponds to the DAG ID, Task ID, execution date and the file respectively
            - uncommand the LogStash output also change the hosts into `logstash` since the service name of LogStash in the docker compose file is `logstash`
                - ```yml
                  output.logstash:
                    # The Logstash hosts
                    hosts: ["logstash:5044"]
                  ```
            - command the hosts line in ElasticSearch output
                - ```yml
                  # output.elasticsearch:
                    # Array of hosts to connect to.
                    # hosts: ["localhost:9200"]
                  ```
            - save the file
        - now we can start the FileBeat by running `./filebeat -e -c filebeat.yml -d "publish"` command
            - this command will start FileBeat based on the configuration file of *filebeat.yml* and enables the debug selector publish to filter the logs of FileBeat
- Go to the Airflow UI and turn on the *logger_dag* DAG and wait for the DAGrun to finish
- Go to the Kibana UI and click *Explore on my own* button
    - from the left pannel click on the management icon
        - click on *Index Management* menu
            - we'll see an index from our Airflow with the current date corresponding to when the logs have been processed
        - click on *Index Patterns* menu and create new index pattern by clicking *Create index pattern* button on the top right
            - type the index pattern with the value of `airflow-logs-*` that should match with our Airflow logs
            - click on *> Next Step* button
            - choose `@timestamp` from the dropdown button for filtering the time field name
            - click on *Create index pattern* button
            - after that we'll obtain the mapping of the log documents so we are able to request those fields from Kibana to make filters, aggregations, statistics and more on the data
    - from the left pannel click on the discover icon
        - on the screen we'll see the log events of our tasks generated from Airflow are stored and queryable from ElasticSearch

<br><br>

## 3. Build Dashboard Using Kibana and ElasticSearch

- First  we need to go to code editor, Airflow UI and Kibana UI then delete all of the histories from *logger_dag* DAG
    - Code editor
        - Remove the *logger_dag* folder on logger/mnt/airflow/logs
    - Airflow UI
        - Turn of *logger_dag* DAG
        - Remove the jobs from *Browse > Jobs*
        - Remove the DAGrun from *Browse > DAG Runs*
    - Kibana UI
        - Remove the existing index on *management > Index Management > Manage index > Delete index*
        - *management > Index Patterns > select the pattern > delete button*
- Go to the Airflow UI and turn on the *data_dag* DAG and wait for the DAGrun to finish
- Go to the Kibana UI
    - from the left pannel click on the management icon
        - click on *Index Management* menu
            - check if the index of the logs is available or not
        - click on *Index Patterns* menu and create new index pattern by clicking *Create index pattern* button on the top right
            - type the index pattern with the value of `airflow-logs-*` that should match with our Airflow logs
            - click on *> Next Step* button
            - choose `@timestamp` from the dropdown button for filtering the time field name
            - click on *Create index pattern* button
    - from the left pannel click on the visualize icon
        - click on *Create new visualization* button
        - in our case we choose the Gauge which indicates if a give value goes beyond a defined threshold
        - choose the pattern that we already created
        - on the left, there are several options that can be customized according to our needs
- Go to the Airflow UI and turn on the *logger_dag* DAG and wait for the DAGrun to finish then go back to the visualize menu on Kibana UI