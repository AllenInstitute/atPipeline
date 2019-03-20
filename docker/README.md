## Instructions to compile AT Pipeline docker images

### Build render-ws

```console
git clone --branch at_develop --single-branch https://github.com/perlman/render.git build/render
# Workaround for maven surefire bug [https://github.com/saalfeldlab/render/issues/95]
cat build/render/Dockerfile  | sed 's|openjdk:8-jdk|openjdk:8u171-jdk|g' > build/Dockerfile-render-ws
docker build -t atpipeline/render-ws:dev -f build/Dockerfile-render-ws build/render
```

### Check out source code

Note: These comands should be run from the ```atPipeline/docker``` directory.

TODO: Figure out how to revert to old git submodule behavior with per-submodule .git directories, which is needed in the build process for render and render-python.[https://github.com/git/git/blob/master/Documentation/RelNotes/1.7.8.txt#L109]

```console
git clone --branch at_develop --single-branch https://github.com/perlman/render.git build/render
git clone --branch master --single-branch git@github.com:AllenInstitute/at_modules.git build/at_modules
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
* _latest_: (default tag) Latest version of (probably) stable builds
* _dev_: Current development images; may be unstable
* _stable_: A known good & test configuration.

TODO: Add specific version numbers (or dates?) to align with ATExplroer distribution.

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

docker push atpipeline/render-ws:dev
docker push atpipeline/atcore:dev
docker push atpipeline/vizrelay:dev
```
### Using the atcore container

The ``atpipeline/atcore`` container keeps render-python, render-modules and at_modules in ```/shared``` for easy developing via using a volume mount to the a local copy of the source code.
