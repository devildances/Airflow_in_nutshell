# ADVANCED CONCEPTS IN APACHE AIRFLOW

Let's imagine that we have multiple files that we want to process, as a best practice we'll have 1 task for each file, and if we have 20 or 30 different files we'll end up with 20 or 30 different tasks.

- How to make our DAG clearer?
    - At first, we might want to do is to group those tasks together where they share the same functionality in order to make our DAG clearer
    - So how can we make our DAG clearer by grouping tasks that having the same functionality?
- How to choose one task or another with conditional?
    - One thing that will be truly useful for us is to be able to choose one task or another according to a condition or value
    - For example, we have some user data and imagine that we also have a subscription service, if a user didn't subscribe to our service then we want to send an email to the user and if a suer already subscribed then we want to execute another task
    - So how can we choose one task or another according to a condition?
- How to exchange data between tasks?
    - We'll have multiple tasks in our data pipeline and we might need to use the output of the previous task in order to move forward with the next task
    - For example, we have T1 and T2 where T2 needs the data from T1
    - How can we do that? How can we share data between those tasks?



## I. No More Repetitive Patterns

As we're going to build complex data pipelines where the problem is the more tasks we add the more difficulty will be to understand our data pipelines. If we have hundreds or thousands of different tasks in a give DAG, as we can imagine from the UI it will be very hard to know which task does what, what are the dependencies and so on. So we definitely have to find a way in order to make our data pipeline clearer. Let's start with a very simple use case as below.

![Alt text](/files/images/img6.png?raw=true "repeat")

So we might have the data pipeline like the image above where the first 3 tasks are in charge of downloading files then we might have another task in the middle for checking the files and last with 3 other tasks in order to process the files with the dependencies as per image. And our goal is *how can we group the tasks that share common functionality (downloading and processing files) in order to have on 1 task of each so that we obtain the following data pipeline like the image below which is already much clearer*?

![Alt text](/files/images/img7.png?raw=true "nonrepeat")

The answer is by using **SubDAGs**. It allows us to create a DAG inside another DAG in order to group our task together.


### I.1. SubDAGs

When we want to implement subDAGs in our data pipeline, we need 2 things:

- we need the subDAGs operator
    ```python
    from airflow.operators.subdag import SubDagOperator
    ```
    - there is 1 special argument that we have to specify which is `subdag`
        - this argument expects a function that return the subDAG
- we need to create a function that return the SubDAG which will be used in `SubDagOperator` object as parameter
    - first, we need to create a new folder named *subdags* inside the folder *dags*
    - in *subdags* folder where we will put the python file that contains the function
    - and in that file we define the function that will return the SubDAG
        - this function expects some arguments
            - `parent_dag_id`
            - `child_dag_id`
            - `default_args`

At this point we have to know that **SubDAGs are not recommended at all in production or even in development stage so WE SHOULD NOT USE SUBDAGS!!**.
There are 3 main reasons why we shouldn't use SubDAGs:

1. We can end up with deadlocks means at some point we might not be able to execute any more tasks in our Airflow instance
2. It quite complex, indeed we have to create a new folder, a new function, then inside that function we create a new DAG sharing the same default arguments at the parent DAG and we have to make sure that the DAG id follow a special notation also we need to use the SubDAG operator inside the parent DAG to call that SubDAG
3. It has their own executor (SequentialExecutor), in that case with the SubDAG that we have just added we use the SequentialExecutor by default even if in the configuration file of Airflow we set LocalExecutor or CeleryExecutor

In fact, there is a new concept that has been introduced in Apache Airflow 2.0 which is definitely easier to use and as powerful as SubDAGs which is the **TaskGroups**.


### I.2. TaskGroups

These are how we implement TaskGroups:

- we need the TaskGroups object
    ```python
    from airflow.utils.task_group import TaskGroup
    ```
- once we have the `TaskGroup` object we're ready to group our tasks together
    - when we instantiate a `TaskGroup` object, we need to specify group id
    - and from there we have to specify the tasks that we want to group together under it

TaskGroups are super powerful and super flexible so forget about SubDAGs and go with TaskGroups.



## II. Exchange Data Between Tasks



## III. Executing by Conditions