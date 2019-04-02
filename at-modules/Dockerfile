#FROM docker.aibs-artifactory.corp.alleninstitute.org/fcollman/render-modules-candidate:multi-channel-correction

FROM openjdk:8-jdk as build_environment

RUN mkdir -p /usr/local/at_modules

WORKDIR /usr/local/at_modules


RUN apt-get -y update 

RUN apt-get -y upgrade

RUN apt-cache show maven | grep Version

RUN apt-get -y install maven

COPY pom.xml .

RUN mkdir -p /usr/local/at_modules/src

WORKDIR /usr/local/at_modules/src

COPY src .

WORKDIR /usr/local/at_modules

ENV _JAVA_OPTIONS -Djdk.net.URLClassPath.disableClassPathURLCheck=true
RUN mvn install
