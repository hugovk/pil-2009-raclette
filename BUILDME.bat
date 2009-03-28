rem # $Id$
rem # call DISTCLEAN
erase PIL\*.pyd
python setup.py build_ext -i
upx --best PIL\*.pyd
