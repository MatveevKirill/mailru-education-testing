FROM python:3.9

WORKDIR /source

COPY ./source .
COPY ./requirements.txt .

RUN pip3.9 install -r requirements.txt

CMD ["pytest", "-v", "--alluredir=/tmp/allure-report", "-n", "3"]