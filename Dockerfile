FROM python:alpine

WORKDIR /
ENV FLASK_RUN_HOST=0.0.0.0

COPY ./ /

RUN apt-get update
RUN apt-get -y install \
    tesseract-ocr \
    tesseract-ocr-jpn
RUN apt-get clean
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
