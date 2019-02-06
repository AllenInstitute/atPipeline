== Instructions to compile AT Pipeline docker images

=== Check out source code

Note: These commands should be run from the ```atPipeline/docker directory```.

TODO: Figure out how to revert to old git submodule behavior with per-submodule .git directories, which is needed in the build process for render and render-python.[https://github.com/git/git/blob/master/Documentation/RelNotes/1.7.8.txt#L109]
TODO: Warm maven cache by 

```console
git clone --branch master --single-branch https://github.com/saalfeldlab/render.git build/render
git clone --branch master --single-branch https://github.com/fcollman/render-python.git build/render-python
git clone --branch at_develop --single-branch https://github.com/AllenInstitute/render-modules.git build/render-modules
git clone --branch at_develop --single-branch https://github.com/AllenInstitute/render-python-apps.git build/render-python-apps
git clone --branch master --single-branch git@github.com:AllenInstitute/at_modules.git build/at_modules
```

=== Build render-ws

```console
# Workaround for maven surefire bug [https://github.com/saalfeldlab/render/issues/95]
cat build/render/Dockerfile  | sed 's|openjdk:8-jdk|openjdk:8u171-jdk|g' > build/Dockerfile-render-ws
docker build -t atpipeline/render-ws -f build/Dockerfile-render-ws build/render
```

=== Build monolithic docker image for ATPipeline

```console
docker build -t atpipeline/atcore -f Dockerfile-atcore build
```

=== Build vizrelay

TBD

=== Build neuroglancer

TBD

=== Push images to Docker hub

Optional, if the images test OK...

```console
docker push atpipeline/render-ws 
docker push atpipeline/atcore

```
