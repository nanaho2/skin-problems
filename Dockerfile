FROM python:alpine

WORKDIR /app
ENV FLASK_RUN_HOST=0.0.0.0

COPY ./app /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["flask", "run", "--host=0.0.0.0"]
