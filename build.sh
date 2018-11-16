#!/bin/bash

EXECUTABLENAME="Http2Mqtt"

mkdir -p out

echo "Cleaning old files"
rm -f "out/$EXECUTABLENAME" "out/$EXECUTABLENAME.zip"

echo "Building"
cd flaskr
zip -r "../out/$EXECUTABLENAME.zip" *
cd ..
echo '#!/usr/bin/env python3' | cat - "out/$EXECUTABLENAME.zip" > "out/$EXECUTABLENAME"
chmod +x "out/$EXECUTABLENAME"
rm "out/$EXECUTABLENAME.zip"
