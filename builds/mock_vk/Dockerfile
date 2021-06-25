FROM python:3.9

WORKDIR /source

ADD requirements.txt requirements.txt
ADD source .

RUN pip install -r requirements.txt

CMD [ "python3.9", "mock.py"]