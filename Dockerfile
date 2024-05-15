FROM python:3.8-slim
RUN apt-get update && apt-get install -y \
	cron \
	supervisor

RUN mkdir -p /var/log/supervisor /etc/supervisor/conf.d
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN sed -i 's/url.parse/urllib.parse/' /usr/local/lib/python3.8/site-packages/amazonify.py
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY crontab.txt /etc/cron.d/bot-crontab
RUN chmod 0644 /etc/cron.d/bot-crontab
RUN crontab /etc/cron.d/bot-crontab
VOLUME ["/var/log/supervisor"]

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
