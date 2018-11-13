docker build -t  sharmi/at_modules .
docker kill atmodules
docker rm atmodules
docker run -d --name atmodules \
-v /nas2:/nas2 \
-v /nas:/nas \
-v /nas3:/nas3 \
-v /nas4:/nas4 \
-v /data:/data \
-v /pipeline:/pipeline \
-v /etc/hosts:/etc/hosts \
-p 7778:7778 \
-i -t sharmi/at_modules \
/bin/bash 
