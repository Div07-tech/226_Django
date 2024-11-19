#!/usr/bin/env bash
pipenv run pipenv install
python website/manage.py collectstatic --no-input
python website/manage.py migrate
