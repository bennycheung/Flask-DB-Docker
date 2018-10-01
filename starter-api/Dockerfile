FROM python:3.5

RUN apt-get update && apt-get install -y vim-tiny

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/
RUN pip install -r requirements.txt

ADD . /app

# EXPOSE 5000
# ENTRYPOINT ["python", "manage.py", "runserver"]
# CMD ["-t", "0.0.0.0", "-p", "5000"]

