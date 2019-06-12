FROM node:12 as build-stage
ARG NG_GIT=https://github.com/perlman/neuroglancer.git 
ARG NG_BRANCH=master
WORKDIR /work
RUN git clone $NG_GIT --branch $NG_BRANCH neuroglancer
WORKDIR /work/neuroglancer
RUN npm install && npm run build-min

FROM nginx:stable
COPY --from=build-stage /work/neuroglancer/dist/min /neuroglancer
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Already in the nginx image:
# EXPOSE 80 
# CMD ["nginx", "-g", "daemon off;"]
