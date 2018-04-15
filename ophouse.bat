@echo off
IF "%~1"=="" echo syntax: "ophouse {-make | -apply | -run}"
IF "%~1"=="-make" python manage.py makemigrations
IF "%~1"=="-apply" python manage.py migrate
IF "%~1"=="-run" python manage.py runserver