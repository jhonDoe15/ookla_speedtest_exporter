FROM python:latest

EXPOSE 2313

ENV PYTHONUNBUFFERED=1

ENV SRC_DIR /usr/bin/src/webapp/src

WORKDIR ${SRC_DIR}

RUN apt update -y && \
    apt install curl && \
    curl -s https://install.speedtest.net/app/cli/install.deb.sh | bash && \ 
    apt install speedtest

#RUN speedtest --accept-license

RUN  mkdir -p /root/.config/ookla/

COPY speedtest-cli.json /root/.config/ookla/

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY main.py .

CMD ["python3", "main.py"]
