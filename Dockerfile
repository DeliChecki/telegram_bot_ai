FROM python:3.9
ADD . /bot
WORKDIR /bot
RUN pip install -r requirements.txt --no-cache-dir --quiet
CMD python run_bot.py