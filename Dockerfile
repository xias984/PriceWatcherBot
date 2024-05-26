FROM python:3.8-slim
RUN apt-get update && apt-get install -y cron supervisor nano procps
RUN mkdir -p /var/log/supervisor /etc/supervisor/conf.d
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY crontab.txt /app/crontab.txt
RUN crontab /app/crontab.txt

VOLUME ["/var/log/supervisor"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
