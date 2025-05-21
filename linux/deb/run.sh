#!/bin/bash

rm -rf kk*

gcc main.c -o kk
mkdir kk-pkg
mkdir -p kk-pkg/DEBIAN
mkdir -p kk-pkg/usr/bin

mv kk kk-pkg/usr/bin/

pushd kk-pkg/DEBIAN

touch postinst
touch postrm
touch changelog
touch control
chmod 775 post*

echo "Source:kk" >> control
echo "Priority:optional" >> control
echo "Maintainer:maker" >> control
echo "Build-Depends:diodon" >> control
echo "Standards-Version:4.0.0" >> control
echo "Version:1.0.0" >> control
echo "Package:kk" >> control
echo "Architecture:amd64" >> control
echo "Description:This package just for test! just print kk world!" >> control

popd

dpkg-deb --build kk-pkg

sudo dpkg -i kk-pkg.deb

















