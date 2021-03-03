#!/bin/bash

case $1 in
    "clean")
        docker system prune
        docker volume remove leistung_db-data
        ;;
esac

docker-compose up --build --scale frontend=2
