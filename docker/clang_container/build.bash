#! /bin/bash

echo "Building.."

lib=dsl/thirdparties
cmake -B"/build/$lib" \
-H"/libs/$lib" \
-G "Ninja" \
-DCMAKE_C_COMPILER="/clang_7.0.1/bin/clang" \
-DCMAKE_CXX_COMPILER="/clang_7.0.1/bin/clang++"   

ninja -C /builds/$lib install

lib=dsl
cmake -B"/build/$lib" \
-H"/libs/$lib" \
-G "Ninja" \
-DCMAKE_C_COMPILER="/clang_7.0.1/bin/clang" \
-DCMAKE_CXX_COMPILER="/clang_7.0.1/bin/clang++"   

ninja -C /builds/$lib install

lib=atExplorer
cmake -B"/build/$lib" \
-H"/libs/$lib" \
-G "Ninja" \
-DCMAKE_C_COMPILER="/clang_7.0.1/bin/clang" \
-DCMAKE_CXX_COMPILER="/clang_7.0.1/bin/clang++"   

ninja -C /builds/$lib install

ldconfig 
echo "Done"



