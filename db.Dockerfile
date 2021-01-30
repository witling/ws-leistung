FROM postgres:9.6

COPY ./script/dbinit.sql /docker-entrypoint-initdb.d/10_init.sql
RUN chmod a+r /docker-entrypoint-initdb.d/*
