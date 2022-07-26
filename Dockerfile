FROM python:3.9.13-slim-buster
ADD . /bot
WORKDIR /bot
RUN pip install -r requirements.txt --no-cache-dir --quiet
CMD python run_bot.py