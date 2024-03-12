# Filename: Dockerfile
FROM alpine:latest
WORKDIR /usr/src/app
COPY *.py ./
RUN apk add --no-cache python3 py3-pip firefox curl
RUN apk update && apk add libpq
RUN apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
RUN pip install requests lxml selenium psycopg2 --break-system-packages	
RUN apk del .build-deps
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz
RUN tar -zxf geckodriver-v0.32.0-linux64.tar.gz -C /usr/bin
RUN curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/26b149cc-4831-4cc6-997d-9e21b9c88a1f/cert'
CMD ["python","./get_atis.py"]
