#! /bin/bash

echo "Building atcore ThirdParty libraries.."

CC=$CC
CXX=$CXX

#Build build files
lib=dsl/ThirdParties
cmake -B"/build/$lib" -H"/libs/$lib" -G "Ninja" \
-DCMAKE_C_COMPILER=$CC \
-DCMAKE_CXX_COMPILER=$CXX   

lib=dsl
cmake -B"/build/$lib" -H"/libs/$lib" -G "Ninja" \
-DCMAKE_C_COMPILER=$CC \
-DCMAKE_CXX_COMPILER=$CXX  

lib=atExplorer
cmake -B"/build/$lib" -H"/libs/$lib" -G "Ninja" \
-DCMAKE_C_COMPILER=$CC \
-DCMAKE_CXX_COMPILER=$CXX  

#Build binaries
ninja -C /build/dsl/ThirdParties install
ninja -C /build/dsl install
ninja -C /build/atExplorer install

#COnfigure runtime paths to shared libraries and apps
ldconfig 


echo "Done Building"
