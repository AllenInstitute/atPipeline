#!/bin/bash

#
# A wrapper to spark-submit to make sure the current userid can resolve.
# Based on:
# https://stackoverflow.com/questions/45198252/apache-spark-standalone-for-anonymous-uid-without-user-name
#

cat /etc/passwd > /tmp/passwd.$(id -u)
echo "$(id -u):x:$(id -u):$(id -g):dynamic uid:$SPARK_HOME:/bin/false" >> /tmp/passwd.$(id -u)

export NSS_WRAPPER_PASSWD=/tmp/passwd.$(id -u)
export NSS_WRAPPER_GROUP=/etc/group
export LD_PRELOAD=libnss_wrapper.so

exec "$@"
