#!/bin/bash

find . -regex "\(*~\|.*__pycache__.*\|*.py[co]\)" -delete
find . -name "*~" -delete

tar --dereference -c -f http-api.tar.gz \
    services \
    conf \
    api.py

docker build -t catenae/erdd-api .
rm -f http-api.tar.gz
docker push catenae/erdd-api
