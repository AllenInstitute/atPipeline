#
# Docker file to build entire AT pipeline software stack into a single container
# Based on
#   https://raw.githubusercontent.com/fcollman/render-deploy/base-image/shared/Dockerfile
#
# TODO: Seperate builders for artifacts
# TODO: Set up continuous integration
#

FROM ubuntu:18.04

# Updating Ubuntu packages
RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install --no-install-recommends wget curl git openjdk-8-jdk ca-certificates-java gcc build-essential vim maven && \
    apt-get -y install --no-install-recommends cmake ninja-build libboost-all-dev clang && \
    apt-get -y install --no-install-recommends libspatialindex-dev

# Install conda
# Based on https://github.com/ContinuumIO/docker-images/blob/master/miniconda/Dockerfile
ENV CONDA_VERSION 4.5.12
ENV CONDA_MD5 4be03f925e992a8eda03758b72a77298

# Create non-root user, install dependencies, install Conda
RUN addgroup --gid 10151 anaconda && \
    adduser --uid 10151 anaconda --ingroup anaconda --disabled-password --gecos "" && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda2-$CONDA_VERSION-Linux-x86_64.sh && \
    echo "${CONDA_MD5}  Miniconda2-$CONDA_VERSION-Linux-x86_64.sh" > miniconda.md5 && \
    if [ $(md5sum -c miniconda.md5 | awk '{print $2}') != "OK" ] ; then exit 1; fi && \
    mv Miniconda2-$CONDA_VERSION-Linux-x86_64.sh miniconda.sh && \
    mkdir -p /opt && \
    sh ./miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh miniconda.md5 && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    chown -R anaconda:anaconda /opt && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /home/anaconda/.profile && \
    echo "conda activate base" >> /home/anaconda/.profile

# USER 10151
ENV PATH $PATH:"/bin:/sbin:/usr/bin:/opt/conda/bin"

RUN conda update conda && conda update python && conda install nomkl

RUN mkdir -p /shared
WORKDIR /shared

# add a simple script that can auto-detect the appropriate JAVA_HOME value
# based on whether the JDK or only the JRE is installed
RUN { \
		echo '#!/bin/sh'; \
		echo 'set -e'; \
		echo; \
		echo 'dirname "$(dirname "$(readlink -f "$(which javac || which java)")")"'; \
	} > /usr/local/bin/docker-java-home \
	&& chmod +x /usr/local/bin/docker-java-home

# do some fancy footwork to create a JAVA_HOME that's cross-architecture-safe
RUN ln -svT "/usr/lib/jvm/java-8-openjdk-$(dpkg --print-architecture)" /docker-java-home

# Spark setup
ENV SPARK_VERSION 2.0.2
ENV SPARK_PACKAGE spark-${SPARK_VERSION}-bin-hadoop2.7
ENV SPARK_HOME /usr/spark-${SPARK_VERSION}
ENV SPARK_DIST_CLASSPATH="$HADOOP_HOME/etc/hadoop/*:$HADOOP_HOME/share/hadoop/common/lib/*:$HADOOP_HOME/share/hadoop/common/*:$HADOOP_HOME/share"
ENV PATH $PATH:${SPARK_HOME}/bin
RUN curl -sL --retry 3 \
"https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop2.7.tgz" \
 | gunzip \
 | tar x -C /usr/ \
&& mv /usr/$SPARK_PACKAGE $SPARK_HOME \
&& chown -R root:root $SPARK_HOME

# Build the render client scripts
ENV JAVA_HOME /docker-java-home
ENV RENDER_JAVA_HOME /docker-java-home
ENV RENDER_CLIENT_SCRIPTS=/shared/render/render-ws-java-client/src/main/scripts

# Install Render
WORKDIR /shared/render/
RUN git clone --branch at_develop --single-branch https://github.com/perlman/render.git /shared/render && \
    mvn clean && mvn -T 1C -Dproject.build.sourceEncoding=UTF-8 package

# Install at_modules
WORKDIR /shared/at_modules
COPY ./at-modules/ /shared/at_modules
RUN mvn install

# Install render-python
WORKDIR /shared/render-python
RUN git clone --branch master --single-branch https://github.com/fcollman/render-python.git /shared/render-python && \
    pip install -e /shared/render-python

# Install render-modules
WORKDIR /shared/render-modules
RUN git clone --branch at_develop --single-branch https://github.com/AllenInstitute/render-modules.git /shared/render-modules && \
    pip install -e /shared/render-modules

# Install render-python-apps
WORKDIR /shared/render-python-apps
RUN git clone --branch at_develop --single-branch https://github.com/AllenInstitute/render-python-apps.git /shared/render-python-apps && \
    pip install -e /shared/render-python-apps

# Copy pipeline files
WORKDIR /pipeline
COPY ./pipeline/ /pipeline

# Build atcli
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
RUN mkdir -p /libs && mkdir -p /build
COPY ./docker/clang-container/third-party-libs /libs
COPY ./docker/clang-container/build-thirdparty-libs.bash /build
WORKDIR /build
RUN bash build-thirdparty-libs.bash

ENV TZ=US/Pacific
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /work
CMD [ "/bin/bash" ]
