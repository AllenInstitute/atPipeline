FROM docker.aibs-artifactory.corp.alleninstitute.org/fcollman/render-modules-candidate:multi-channel-correction

RUN mkdir -p /usr/local/at_modules

WORKDIR /usr/local/at_modules


RUN apt-get -y update 

RUN apt-get -y upgrade

RUN apt-cache show maven | grep Version

RUN apt-get -y install maven

COPY pom.xml .

RUN mvn install
