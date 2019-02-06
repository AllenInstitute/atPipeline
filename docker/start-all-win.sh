#! /usr/bin/bash
BUILD=${1:-false}
echo "Build flag is "$BUILD

#Render Service, mongo & ndviz stuff
sh ./start-render-services.sh $BUILD

#AT MODULES
sh ./start-atmodules-windows.sh $BUILD

#RENDER PYTHON APPS (MULTCHAN branch) 
sh ./start-atcore-windows.sh $BUILD


echo "Done.."
