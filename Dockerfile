FROM ubuntu:22.04.01

WORKDIR /app

COPY ./app /app

RUN apt-get update && rm -rf /var/lib/apt/lists/* && apt-get install -y software-properties-common --no-install-recommends
RUN add-apt-repository ppa:alex-p/tesseract-ocr5
RUN apt-get update && rm -rf /var/lib/apt/lists/* && apt-get install -y tesseract-ocr libtesseract-dev --no-install-recommends
RUN apt-get update && rm -rf /var/lib/apt/lists/* && apt-get install -y python3 python3-pip --no-install-recommends
RUN apt-get clean
RUN pip3 install pyocr
RUN pip install -r /app/requirements.txt

CMD ["python3", "[app.py](http://app.py/)"]