# Instructions to compile new docker images

## Build containers

These instructions are for building the atPipeline containers.
Commands should be run in the `docker` directory.

### Build render-ws
```console
git clone --branch at_develop --single-branch https://github.com/perlman/render.git build/render
docker build -t atpipeline/render-ws:dev build/render
```

### Build monolithic docker image for ATPipeline

```console
docker build -t atpipeline/atcore:dev ..
```

### Build vizrelay
```console
git clone --branch master --single-branch https://github.com/perlman/vizrelay build/vizrelay
docker build -t atpipeline/vizrelay:dev -f build/vizrelay/Dockerfile build/vizrelay
```

### Build neuroglancer
```console
docker build -t atpipeline/neuroglancer:dev neuroglancer-nginx
```

## Push images to Docker hub

Suggested tag use:
* _latest_: (default tag) Latest version of (probably) stable builds.
* _dev_: Current development images; may be unstable.
* _X.Y.Z_: Tag with the current version of the code (from VERSION.txt).

```console
docker push atpipeline/render-ws:dev
docker push atpipeline/atcore:dev
docker push atpipeline/vizrelay:dev
docker push atpipeline/neuroglancer:dev
```

If you want to declare these images as latest:
```console
docker tag atpipeline/render-ws:dev atpipeline/render-ws
docker tag atpipeline/atcore:dev atpipeline/atcore
docker tag atpipeline/vizrelay:dev atpipeline/vizrelay
docker tag atpipeline/neuroglancer:dev atpipeline/neuroglancer

docker push atpipeline/render-ws
docker push atpipeline/atcore
docker push atpipeline/vizrelay
docker push atpipeline/neuroglancer
```

...or to push with the version number:
```console
docker tag atpipeline/render-ws:dev atpipeline/render-ws:`cat VERSION.txt`
docker tag atpipeline/atcore:dev atpipeline/atcore:`cat VERSION.txt`
docker tag atpipeline/vizrelay:dev atpipeline/vizrelay:`cat VERSION.txt`
docker tag atpipeline/neuroglancer:dev atpipeline/neuroglancer:`cat VERSION.txt`

docker push atpipeline/render-ws:`cat VERSION.txt`
docker push atpipeline/atcore:`cat VERSION.txt`
docker push atpipeline/vizrelay:`cat VERSION.txt`
docker push atpipeline/neuroglancer:`cat VERSION.txt`
```

## Using the atcore container for development

The `atpipeline/atcore``container keeps render-python, render-modules and at_modules in ```/shared``` for easy development via volume mounts to the a local copy of the libraries.
