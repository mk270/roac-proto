FROM python:3

RUN apt-get update && apt-get upgrade -y

WORKDIR /usr/src/app

COPY ./ ./
RUN pip3 install setuptools --upgrade && \
    pip3 install -r requirements.txt && \
    rm requirements.txt

EXPOSE 80

CMD ["python3", "src/serve.py"]
