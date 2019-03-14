FROM python:2.7.15-stretch

RUN apt update && apt install -y software-properties-common && add-apt-repository -y ppa:webupd8team/java && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C2518248EEA14886 && echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" > /etc/apt/sources.list.d/webupd8team-ubuntu-java-disco.list && apt update && echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && apt install -y oracle-java8-installer
COPY requirements.txt ./
#RUN pip install --no-cache-dir --proxy 135.245.192.7:8000 -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app

RUN cd /app && pip install -e .
