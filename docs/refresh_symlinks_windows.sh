#!/usr/bin/bash

# Run this in gitbash with administrator rights, if you are on windows
# and the docs won't build properly.
export MSYS=winsymlinks:nativestrict
rm readme.md
rm history.md
ln -s ../README.md readme.md
ln -s ../HISTORY.md history.md
