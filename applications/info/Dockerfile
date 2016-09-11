FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    python \
    build-essential \
    python-pip \
    python-setuptools

COPY dist/Info_Server-0.0.1.tar.gz /tmp/Info_Server-0.0.1.tar.gz

RUN bash -c 'mkdir -p /root/server/{conf,logs}' && tar zxf /tmp/Info_Server-0.0.1.tar.gz -C /root/server --strip-components=1

RUN touch /root/server/logs/server.log

COPY conf/app_info.json conf/app_info.json

WORKDIR /root/server/

RUN python setup.py install

EXPOSE 8000

# CMD /usr/local/bin/info_server.py -p 8000 -l /root/server/logs/server.log -i /root/server/conf/app_info.json
