# %% import all the libraries and modules that we need

# Initiate - the DAG object is actually our data pipeline so we need to import it first
from email import message
from airflow import DAG
from datetime import datetime, timedelta

# 1st task - since we'll use Sensor Operator then we need to import it as well from HTTP's provider
from airflow.providers.http.sensors.http import HttpSensor

# 2nd task - we need to import File Sensor
from airflow.sensors.filesystem import FileSensor

# 3rd task - in order to use Python function then we need Python Operator to be imported
from airflow.operators.python import PythonOperator
import csv, requests, json

# 4th task - we need the operator that can run bash command
from airflow.operators.bash import BashOperator

# 5th task - since we'll create new table in Hive then we need Hive Operator in order to do that
from airflow.providers.apache.hive.operators.hive import HiveOperator

# 6th task - we use Spark Operator to process the data rather than Python Operator in Airflow to avoid memory overflow error
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

# 7th task - we need Email Operator so we can send an email notification
from airflow.operators.email import EmailOperator

# 8th task - import specific Operator for us to enable send a notification via Slack
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

# %% additional functions

# 3rd task - define a specific Python function to download forex rates according to the currencies we want to watch
def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')

def _get_message() -> str:
    return "error from forex_data_pipeline"

# %% start the code

# Initiate - define the default arguments for our DAG object that'll be applied on all of our tasks
default_args = {
    "owner" : "airflow",
    "email_on_failure" : False,
    "email_on_retry" : False,
    "email" : "dr.dslearn@gmail.com",
    "retries" : 1,
    "retry_delay" : timedelta(minutes=5)
}

# Initiate - instantiate the DAG object
with DAG("forex_pipeline", start_date=datetime(2022,1,1),
        schedule_interval="@daily", default_args=default_args,
        catchup=False
        ) as dag:

    # 1st task - this task will check if the URL/API is available or not
    is_forex_rates_available = HttpSensor(
        task_id = "is_forex_rates_available",
        http_conn_id = "forex_api",
        endpoint = "marclamberti/f45f872dea4dfd3eaa015a4a1af4b39b",
        response_check = lambda response: "rates" in response.text,
        poke_interval = 5,
        timeout = 20
    )

    '''
    1ST TASK
    on the 1st task, we need to run start.sh script in order to create http_conn_id
    from the Airflow UI so we can connect to the URL/API later when the task is running.
    Go to connection page under Admin menu and after that add new connection with the
    following values:
    Conn Id : forex_api
    Conn Type : HTTP
    Host : https://gist.github.com/

    Run "docker exec -it <container_id> /bin/bash" where the container ID is coming
    from Airflow container to test our 1st task directly through Airflow CLI with
    "airflow tasks test forex_pipeline is_forex_rates_available 2022-01-01" command
    >>> "airflow tasks test <DAG_id> <task_id> <start_date>"
    '''

    # 2nd task - this task in charge of checking if a specific file is available or not at a specific location in our file system
    is_forex_currencies_file_available = FileSensor(
        task_id = "is_forex_currencies_file_available",
        fs_conn_id = "forex_path",
        filepath = "forex_currencies.csv",
        poke_interval = 5,
        timeout = 20
    )

    '''
    2ND TASK
    Open the Airflow UI and create new connection to add our specific location
    in our file system that contains the forex file with the following values:
    Conn Id : forex_path
    Conn Type : File (path)
    Extra : {"path":"/opt/airflow/dags/files"}

    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''

    # 3rd task - this task will download the forex rate from the URL/API
    downloading_rates = PythonOperator(
        task_id = "downloading_rates",
        python_callable = download_rates
    )

    '''
    3RD TASK
    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''

    # 4th task - this task will save the file that is generated from the 3rd task into HDFS
    saving_rates = BashOperator(
        task_id = "saving_rates",
        bash_command = """
        hdfs dfs -mkdir -p /forex && \
        hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
        """
    )

    '''
    4TH TASK
    To open the Hue through web browser we can just open the link localhost:32762
    username : root
    password : root

    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''

    # 5th task - this task will create (ONLY) the Hive table (WITHOUT THE DATA) related to the forex_rates.json in our HDFS
    creating_forex_rates_table = HiveOperator(
        task_id="creating_forex_rates_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    '''
    5TH TASK
    Open the Airflow UI and create new Hive connection so we can
    communicate with Hive with the following values:
    Conn Id : hive_conn
    Conn Type : Hive Server 2 Thrift
    host : hive-server
    login : hive
    password : hive
    port : 10000

    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''

    # 6th task - this task will process the forex rates and put it into Hive table that just created in 5th task
    forex_processing = SparkSubmitOperator(
        task_id = "forex_processing",
        application = "/opt/airflow/dags/scripts/forex_processing.py",
        conn_id = "spark_conn",
        verbose = False
    )
    '''
    6TH TASK
    Open the Airflow UI and create new Spark connection so we can
    use Spark to process the big data with the following values:
    Conn Id : spark_conn
    Conn Type : Spark
    host : spark://spark-master
    port : 7077

    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''

    # # 7th task - this task responsible to send an email notif when any error occurs
    # send_email_notif = EmailOperator(
    #     task_id = "send_email_notif",
    #     to = "dr.dslearn@gmail.com",
    #     subject = "forex_data_pipeline",
    #     html_content = "<h2>forex_data_pipeline notification</h2>"
    # )

    '''
    7TH TASK
    The way for us to be able to send an email notification we need to generate the token
    first through https://security.google.com/settings/security/apppasswords, after we get
    the token then open the airflow.cfg file to modify the settings corresponding to the
    SMTP protocol and look for smtp variable to set some variables of SMTP:
    smtp_host = smtp.gmail.com
    smtp_user = <our email address>
    smtp_password = <our generated token>
    smtp_port = 587
    smtp_mail_from = <our email address>

    since we change the configuration of airflow.cfg we need to restart our Airflow instance
    in our docker cluster by running "docker-compose restart airflow" command.

    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''

    # # 8th task - this task will send a notification message through Slack for specific channel in specific workspace
    # send_slack_notif = SlackWebhookOperator(
    #     task_id = "send_slack_notif",
    #     http_conn_id = "slack_conn",
    #     message = _get_message(),
    #     channel = "$<our channel name>"
    # )

    '''
    8TH TASK
    Open the Slack apps and go to the workspace that we want to use, go to the api.slack.com/apps
    on the browser to create a Slack app that will be used for our Airflow hook (set the App Name and
    select the workspace we want to use) then verify the feature Incoming Webhooks is activated
    (ON status and click 'Add New Webhook to Workspace' button then choose sepcific channel) and copy
    that Webhook URL.

    Open the Airflow UI and create new Slack connection so we can send a notification to Slack channel
    with the following values:
    Conn Id : slack_conn
    Conn Type : HTTP
    password : <Slack Webhook URL>

    *NOTE : We always have to check the task is running well or not manually
            from Airflow CLI before we run it through the Airflow DAG
    '''


    is_forex_rates_available >> is_forex_currencies_file_available >> downloading_rates
    downloading_rates >> saving_rates >> creating_forex_rates_table >> forex_processing
    # forex_processing >> [send_email_notif, send_slack_notif]