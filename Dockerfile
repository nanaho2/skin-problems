FROM python:alpine

WORKDIR /
ENV FLASK_RUN_HOST=0.0.0.0

COPY ./ /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["flask", "run", "--host=0.0.0.0"]
