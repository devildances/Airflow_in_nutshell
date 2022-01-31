#!/bin/bash

docker-compose -f docker-compose-CeleryExecutorELK.yml down
docker-compose -f docker-compose-CeleryExecutorELK.yml up -d