FROM centos:7
# change default C to en_US
# Fix UnicodeEncodeError: 'ascii' codec can't encode
ENV LANG en_US.UTF-8

RUN yum update -y; yum clean all
RUN yum -y install gcc epel-release python3 python3-devel gcc-c++ kernel-devel
RUN yum -y install libnfs-devel
WORKDIR /app
RUN pip3 install -U pip setuptools 
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY /app .
CMD [ "python3", "app.py"]
