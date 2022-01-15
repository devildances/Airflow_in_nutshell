# Build Airflow using Docker with Celery executor

Apache Airflow has 3 core components (meta database, webserver and scheduler) so we'll have 3 different Docker containers that we have to orchestrate in order to run Airflow.

> This project is contained in *airflow_docker* folder.

- Download Docker compose file from Apache Airflow website by running this `wget https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml` command
    - if we don't have `wget` on our local then we can download it via brew by using this `brew install wget` command
- Run the YAML file with `docker-compose -f docker-compose.yaml up -d` command
- Check all running containers using `docker ps` command
- Open the Airflow UI through web browser (localhost:8080)