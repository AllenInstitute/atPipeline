## Instructions to compile AT Pipeline docker images

### Build render-ws

```console
git clone --branch at_develop --single-branch https://github.com/perlman/render.git build/render
docker build -t atpipeline/render-ws:dev build/render
```

### Build monolithic docker image for ATPipeline

```console
# Build with the context of this entire git repo.
docker build -t atpipeline/atcore:dev .
```

### Build vizrelay
```console
git clone --branch master --single-branch https://github.com/perlman/vizrelay build/vizrelay
docker build -t atpipeline/vizrelaydev -f build/vizrelay/Dockerfile build/vizrelay
```

### Build neuroglancer

TBD

### Push images to Docker hub

Suggest tag use:
* _latest_: (default tag) Latest version of (probably) stable builds.
* _dev_: Current development images; may be unstable.
* _dev-YYMMDD_: Tag with specific date of dev build.
* _stable_: A known good & test configuration.


```console
docker push atpipeline/render-ws:dev
docker push atpipeline/atcore:dev
docker push atpipeline/vizrelay:dev
```

If you want to declare these images as latest:
```console
docker tag atpipeline/render-ws:dev atpipeline/render-ws
docker tag atpipeline/atcore:dev atpipeline/atcore
docker tag atpipeline/vizrelay:dev atpipeline/vizrelay

docker push atpipeline/render-ws
docker push atpipeline/atcore
docker push atpipeline/vizrelay
```

...or to push with today's date:

```console
docker tag atpipeline/render-ws:dev atpipeline/render-ws:dev-`date +"%y%m%d"`
docker tag atpipeline/atcore:dev atpipeline/atcore:dev-`date +"%y%m%d"`
docker tag atpipeline/vizrelay:dev atpipeline/vizrelay:dev-`date +"%y%m%d"`

docker push atpipeline/render-ws:dev-`date +"%y%m%d"`
docker push atpipeline/atcore:dev-`date +"%y%m%d"`
docker push atpipeline/vizrelay:dev-`date +"%y%m%d"`
```


Or to push with today's date:



### Using the atcore container

The ``atpipeline/atcore`` container keeps render-python, render-modules and at_modules in ```/shared``` for easy developing via using a volume mount to the a local copy of the source code.
