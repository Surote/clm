FROM ubuntu:18.04 AS build
RUN apt update -y
RUN apt install wget python-dev swig autoconf python3 libtool make -y
WORKDIR /apps/build
RUN  wget https://github.com/sahlberg/libnfs/archive/libnfs-1.10.0.tar.gz
RUN tar -xzf libnfs-1.10.0.tar.gz
WORKDIR /apps/build/libnfs-libnfs-1.10.0/
RUN ls -la ./
RUN pwd
RUN ./bootstrap
RUN ./configure --prefix=/usr
RUN make
#RUN make install
 
FROM ubuntu:18.04
ENV TZ Asia/Bangkok
ENV LANG en_US.UTF-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY --from=build /apps/build/libnfs-libnfs-1.10.0 /apps/build/libnfs-libnfs-1.10.0
WORKDIR /apps/build/libnfs-libnfs-1.10.0/
RUN apt update -y
RUN apt-get -y install locales
RUN apt install make libtool -y
RUN make install
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python3.8 python3-pip -y
RUN apt install build-essential libssl-dev libffi-dev python-dev -y 
RUN ln -s /usr/bin/pip3 /usr/bin/pip
#RUN ln -s /usr/bin/python3.8 /usr/bin/python

WORKDIR /apps/
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install setuptools-rust
RUN pip3 install -r requirements.txt
COPY /app .
#COPY .env .
#RUN pip install libnfs
#RUN pip install jinja2
#RUN pip install elasticsearch
#RUN pip install pytz
RUN rm -rf /apps/build/
CMD [ "python3", "app.py"]