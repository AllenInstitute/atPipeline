#! /bin/bash

echo "Building.."

export PATH=/clang_7.0.1/bin:$PATH
export LD_LIBRARY_PATH=/clang_7.0.1/lib:LD_LIBRARY_PATH
export CC=/clang_7.0.1/bin/clang
export CXX=/clang_7.0.1/bin/clang++

lib=dsl/ThirdParties
cmake -B"/build/$lib" \
-H"/libs/$lib" \
-G "Ninja" \
-DCMAKE_C_COMPILER="/clang_7.0.1/bin/clang" \
-DCMAKE_CXX_COMPILER="/clang_7.0.1/bin/clang++"   

ninja -C /build/$lib install

lib=dsl
cmake -B"/build/$lib" \
-H"/libs/$lib" \
-G "Ninja" \
-DCMAKE_C_COMPILER="/clang_7.0.1/bin/clang" \
-DCMAKE_CXX_COMPILER="/clang_7.0.1/bin/clang++"   

ninja -C /build/$lib install

lib=atExplorer
cmake -B"/build/$lib" \
-H"/libs/$lib" \
-G "Ninja" \
-DCMAKE_C_COMPILER="/clang_7.0.1/bin/clang" \
-DCMAKE_CXX_COMPILER="/clang_7.0.1/bin/clang++"   

ninja -C /build/$lib install

ldconfig 
echo "Done"
