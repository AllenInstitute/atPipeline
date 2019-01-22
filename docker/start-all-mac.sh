#! /usr/bin/bash
BUILD=${1:-false}
echo "Build flag is "$BUILD

#Render Service, mongo & ndviz stuff
sh ./start-render-services.sh $BUILD

#AT MODULES
sh ./start-atmodules-mac.sh $BUILD

#RENDER PYTHON APPS (both multichan and master branches) 
sh ./start-rpa-mac.sh $BUILD

echo "Done.."
