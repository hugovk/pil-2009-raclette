rem # $Id$
rem # quick windows build (for lazy programmers).  for more
rem # information on the build process, see the README file.
erase PIL\*.pyd
python setup.py build_ext -i
rem # upx --best PIL\*.pyd
