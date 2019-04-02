#!/bin/sh

set -e

stripQuotes() {
  echo $* | sed -e 's/^"//' -e 's/"$//'
}

exec "$@"