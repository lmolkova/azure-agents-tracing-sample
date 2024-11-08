FROM python:3.11

EXPOSE  8000
RUN apt-get update && apt-get install -y git && apt-get clean
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]