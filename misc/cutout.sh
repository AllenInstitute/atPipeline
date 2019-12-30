#!/bin/bash

#
# This is a basic shell script to save a png stack from rendef.
#
# Teated on macOS 10.15.12 with no additional requirements.
#

#
# Example URL:
# http://localhost:8080/render-ws/v1/owner/eric/project/M33Quarter/stack/S1_FineAligned_Registered_Merged/z/1/box/4096,0,2048,2048,0.5/png16-image?channels=DAPI_2

RENDER_BASE=http://localhost:8080/render-ws/v1
RENDER_OWNER=eric
RENDER_PROJECT=M33Quarter
RENDER_STACK=S1_FineAligned_Registered_Merged
BASE_X=0
BASE_Y=0
WIDTH=4096
HEIGHT=4096
BASE_Z=0
SECTIONS=2
CHANNELS=(DAPI_1 DAPI_2)

SUFFIX=png
FORMAT=png16-image

for channel in "${CHANNELS[@]}"; do
    for ((z=BASE_Z; z < $BASE_Z+$SECTIONS; z++)); do
        URL=$RENDER_BASE/owner/$RENDER_OWNER/project/$RENDER_PROJECT/stack/$RENDER_STACK/z/$z/box/4096,0,2048,2048,0.5/$FORMAT?channels=$channel
        FILENAME=${channel}.${z}.${SUFFIX}
        curl $URL > $FILENAME
    done
done
