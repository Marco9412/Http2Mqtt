FROM python:3-alpine3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8886

CMD [ "python3", "./Http2Mqtt.py", "./resources/settings.json" ]
