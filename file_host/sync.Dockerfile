FROM python:slim
RUN apt-get update && apt-get -y install cron
RUN (crontab -l ; echo "* * * * * echo Hello world > /proc/1/fd/1 2>/proc/1/fd/2") | crontab
