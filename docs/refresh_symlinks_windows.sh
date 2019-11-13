#!/usr/bin/bash

# Run this in gitbash with administrator rights, if you are on windows
# and the docs won't build properly.
export MSYS=winsymlinks:nativestrict
ln -srf ../README.md readme.md
ln -srf ../HISTORY.md history.md
