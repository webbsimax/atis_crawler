# Filename: Dockerfile
FROM alpine:latest
WORKDIR /usr/src/app
COPY *.py ./
RUN apk add --no-cache python3 py3-pip firefox git
RUN pip install requests lxml selenium mysql-connector
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz
RUN tar -zxf geckodriver-v0.32.0-linux64.tar.gz -C /usr/bin
RUN git clone https://github.com/webbsimax/atis_crawler.git
CMD ["python","./get_atis.py"]
