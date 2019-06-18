#!/bin/bash

#
# A wrapper to spark-submit to make sure the current userid can resolve
# Credit to:
# https://stackoverflow.com/questions/45198252/apache-spark-standalone-for-anonymous-uid-without-user-name
#

cat /etc/passwd > /tmp/passwd
echo "$(id -u):x:$(id -u):$(id -g):dynamic uid:$SPARK_HOME:/bin/false" >> /tmp/passwd

export NSS_WRAPPER_PASSWD=/tmp/passwd
# NSS_WRAPPER_GROUP must be set for NSS_WRAPPER_PASSWD to be used
export NSS_WRAPPER_GROUP=/etc/group

export LD_PRELOAD=libnss_wrapper.so

exec "$@"
