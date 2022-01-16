## 1. start_date and schedule_interval parameters

- **start_date** : the date from which tasks of our DAG can be scheduled and triggered
- **schedule_interval** : the interval of time from the min (**start_date**) at which our DAG should be triggered

> The DAG [X] starts being scheduled from the **start_date** and will be triggered after every **schedule_interval**

<img src="/files/images/img22.png" height="55%" width="55%" />


**execution_date** is:

- NOT the date when the DAG has been run
- corresponds to the begining of the processed period (**start_date** - **schedule_interval**)

> IMPORTANT : A DAG with a **start_date** at 10AM and a **schedule_interval** of 10 minutes, gets really executed at 10:10 for data coming from 10AM.

As a best practice, set the **start_date** globally at the DAG level (through **default_args** using datetime object such as `datetime.datetime(2022,9,1)` with (yyyy,m,d) format) and don't use dynamic values such as `datetime.now()`. We can define the **schedule_interval** either with cron expressions (ex: `0 * * * *`) or timedelta objects (ex : `datetime.timedelta(days=1)`) but as a best practice we should use cron expressions rather than timedelta objects.

<img src="/files/images/img23.png" height="50%" width="50%" />



## 2. Backfill and Catchup



## 3. Dealing with Timezones



## 4. 