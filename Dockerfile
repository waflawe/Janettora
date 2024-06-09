FROM python:3.11-slim

RUN mkdir Janettora
WORKDIR Janettora

ADD requirements/prod.txt /Janettora/requirements.txt
RUN pip install -r requirements.txt

ADD . /Janettora/
ADD .env.docker /Janettora/.env

RUN mkdir .logs/

CMD sleep 10; python database/words_example.py; python bot/bot.py
