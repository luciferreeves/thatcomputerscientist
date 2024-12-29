FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3 python3-pip python3-dev libffi-dev libssl-dev python3-venv

RUN mkdir -p /shifoo

WORKDIR /shifoo

COPY . /shifoo

RUN pip3 install -r requirements.txt

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["sh", "entrypoint.sh"]
