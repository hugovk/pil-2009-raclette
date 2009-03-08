rem # $Id$
rem # call DISTCLEAN
python setup.py build_ext -i
upx --best PIL/*.pyd
