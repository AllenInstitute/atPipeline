FROM docker.aibs-artifactory.corp.alleninstitute.org/fcollman/render-modules-candidate:multi-channel-correction

RUN mkdir -p /usr/local/at_modules

WORKDIR /usr/local/at_modules

RUN mvn compile
