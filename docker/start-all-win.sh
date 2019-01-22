#! /usr/bin/bash
BUILD=${1:-false}
echo "Build flag is "$BUILD

#Render Service, mongo & ndviz stuff
sh ./start-render-services.sh $BUILD

#AT MODULES
sh ./start-atmodules-windows.sh $BUILD

#RENDER PYTHON APPS (MULTCHAN branch) 
sh ./start-rpa-windows.sh $BUILD

#RENDER PYTHON APPS MASTER BRANCH
sh ./start-rpa-master-windows.sh $BUILD

echo "Done.."
