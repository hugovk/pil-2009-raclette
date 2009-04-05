rem # $Id$
erase PIL\*.pyd
python setup.py build_ext -i
rem # upx --best PIL\*.pyd
